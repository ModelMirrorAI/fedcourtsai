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

This doc fixes vocabulary and seams. It is the design; the implementation follows
it without further design decisions.

## Why salience

Today prediction scope is a hard court predicate (`court == "scotus"`) plus the
shared exclusion rules, and **every** in-scope cert petition runs the full
predict/evaluate tournament equally. The agentic stages cost one to two orders of
magnitude more than ingestion, and predicting the whole cert denominator equally
spends that budget on thousands of petitions that will be denied as a matter of
course. A salience-ordered scope keeps the hard eligibility filters, then **ranks**
eligible petitions by a cheap deterministic score and spends the tournament on the
most salient slice up to a fundable **capacity `N`**.

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

- **Tier 0 — hard eligibility (deterministic, at the row).** The existing
  `corpus.OUT_OF_SCOPE_RULES`, evaluated through `out_of_scope_reason_full`, plus
  one new rule: exclude **pro se / in-forma-pauperis** petitions. Fee class is
  derivable — IFP serials start at `IFP_SERIAL_BASE` (`5001`) in the SCOTUS docket
  number (`supremecourt.parse_scotus_docket_number`), so the rule is a row-only
  predicate needing no new column. This is a **documented scope decision** — a
  named rule in `OUT_OF_SCOPE_RULES`, surfaced on the salience board (below), not a
  silent drop: IFP grants are rare but non-zero (Gideon arrived IFP), so excluding
  them is a deliberate, recorded choice, not a claim that IFP cases never matter. A Tier-0 exclusion means *never predict, and prune
  any prediction already committed* — the same destructive-on-purpose semantics
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
written only by a new deterministic pass — `reconcile-salience-selection`,
structurally analogous to the scope reconcile — carries the decision:

1. **Cohort key = `distributed_for_conference`.** Capacity is a *per-conference*
   fundable slice, not a global one. This is what makes replay tractable: "why this
   case and not that one" is always answered within one conference's candidate pool
   at a fixed score version.
2. **Score** every Tier-0-eligible SCOTUS row in the cohort (`salience_score`,
   `salience_version`).
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

- `predict-matrix`'s scope filter gains one skip branch — a hard-in-scope SCOTUS
  docket with `salience_selected == 0` is dropped from the tournament matrix with a
  distinct "not selected this salience round" note (read-time, non-destructive).
- The pull queue declines to enqueue unselected cases.
- **Cleanup stays keyed to hard-scope only.** It never consults `salience_selected`;
  a below-cap-but-hard-in-scope case keeps its committed predictions and simply
  gets no *new* ones.
- **Fail-open**: a legacy row with `salience_selected` unset is treated as
  *selected*, so nothing already committed is ever stranded.

## Capacity `N` — the funding knob

`N` is the single parameter that scales inference cost, and the mechanism the
budget's "more funding = more cases" equation and the milestones' funding milestone
both hang on. It is a **per-conference** config value, and raising it **deepens the
salience-ranked slice rather than changing the ranking**. The **OT2026 default** is
sized to the **bootstrapping** budget — the flagship three-engine long-conference
release fits the ~$10K envelope (~$5K inference at the measured
~$25/fully-tournamented-case): **~150 per regular conference and ~200 for the long
conference** (which clears the summer backlog of 1,000+ petitions at once). A
per-conference cap
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
  skill-vs-baseline column; the ops dashboard reports the selected segment's size,
  its base grant rate, and predictions-vs-baseline.

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
  seam reads it back to drive selection. The **full candidate pool** — including
  Tier-0-excluded and below-cap cases that have no committed directory — lives on
  the `metrics/salience` board, not here.
- **The selection is driven by the `salience_selected` corpus latch**, not by
  reading `scope.json`. `predict-matrix`'s scope filter consumes the latch
  directly, the same way it consumes `predict_excluded` and the court predicate
  today.
- **Hard eligibility** stays in `corpus.OUT_OF_SCOPE_RULES` /
  `out_of_scope_reason_full` (the IFP rule joins here). Below-cap selection is a
  **separate** latch and never enters this evaluator.
- **The salience ranking** is published as a deterministic board under
  `metrics/salience.{json,md}`, regenerated like the other roll-ups — the
  pre-registered big-case board, carrying the ranking, the selected set, and the
  segment base rate.

## Ratified decisions (config, tunable)

The knobs are settled for the first release; each is config, so changing one is a
config edit, not a redesign. `N` **is a guaranteed floor, not a hard ceiling** —
the posture below keeps selection additive and never destructive:

- **Capacity `N`** — per-conference, OT2026 default ~150 / regular conference and
  ~200 / long conference (the bootstrapping envelope above).
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
- **The `big_case` grade is rank-agreement across the cohort** (bigness is
  comparative), with a per-case absolute delta kept only as a secondary diagnostic.
