# Decomposing a predicted outcome

A binary grant/deny forecast carries at most one bit, and the base rate consumes
most of it. What a strong forecast actually delivers — the vote split, who writes,
which doctrinal ground the majority rests on, what a concurrence splits off — is
worth far more, and none of it is scored by a disposition label. This document
defines the decomposition that makes those parts scoreable, and the rule that
scores them.

**The mechanical family is implemented at all three stages; everything else here
is pre-registration — with one carve-out, the
semantic family, which is declared but neither pre-registered nor producing
anything.** The scoring rule is `pipeline.base_rates.claim_score`; the
declared sets — five cert-stage claims under `cert-v2`, carried by every
declared cert moment, four interim claims under `interim-v1` carried by every
interim moment, and the one merits claim (`judgment-disturbed`) under
`merits-v1`, carried by every declared merits moment — live
in `pipeline.claims`, with the resolvers, the strictly-prior baselines, and the
availability mask beside it; `Prediction.claims` carries the predictor's
probabilities and `Evaluation.claim_scores` the harness-computed block. The
first set proposed against the rule was specified in a way that did not
resolve, and *A claim set that failed* records why, in detail, because its
tests are what the declared sets were chosen against. The merits vote,
split, and writing claims remain pre-registered only —
`docs/decision-model.md` records why the vote claims failed the tests. The
semantic family is declared but not pre-registered: `semantic-v1` (*The
semantic family, alpha*) declares two claims on the merits moments and is an
**alpha** — a methodology that has never met an opinion, explicitly not a
commitment of the kind the rest of this document makes. It is elicited and
graded — the predict prompt asks a merits cell for the two propositions and the
evaluate prompt asks a grader for the grades — and it still produces nothing:
no opinion body is ingested to grade against, so every declared claim masks.

Everything else — the whole document up to *The semantic family, alpha* — is
pre-registration: the decomposition and the rule are settled before there is
data to fit them to, which is the only order in which the choice of rule is
credible. That last section is the exception, and says so at its own head; no published
number depends on it, and it is superseded rather than edited.

## Naming

The two families are **mechanical** and **semantic**, after what distinguishes
them: whether resolving a claim needs a reader.

They are deliberately not called tiers. "Tier" is already overloaded three ways —
the salience gate's funnel (`docs/salience.md`), the grant-likelihood band the
prompts and statpack schema call a tier, and an upstream API rate-limit tier in
`config/tracking.yaml`. A fourth meaning would not survive contact.

This is also not a "claim taxonomy", though that phrase fits it. That term is
already spoken for: `metrics/docket.md` and `metrics/README.md` use it for a
subject-matter classification of the questions presented — what petitions are
*about* — which is a different problem with its own vocabulary
(`docs/qp-topic.md`). This document decomposes a predicted *outcome* into
scoreable propositions.

## What a claim is

A **claim** is a proposition about a case's outcome that

1. resolves to true or false from a source fixed before the prediction is scored,
2. carries the predictor's probability that it is true, and
3. has a **baseline** probability computed by the harness from history strictly
   prior to the prediction, never supplied by the predictor.

All three are load-bearing. Without (1) a claim is rhetoric. Without (2) it
cannot be properly scored. Without (3) there is nothing to beat — and if the
predictor sets the baseline, the rule is trivially gamed.

Condition (1) binds the baseline as well as the outcome: both have to be fixed
before scoring, or a claim resolves against a moving target. That is a live
constraint rather than a formality, because the cert-stage signals below live in
mutable corpus columns — see *What is scoreable today*.

Every claim in the declared set is answered. There is no declining, for reasons
set out under *Why the set is mandatory*.

### Mechanical claims

Resolved in code, no reader and no latitude. They split by the event's stage,
because a claim is only scoreable where its stage's outcome record carries the
signal it resolves against.

**Cert-stage** — the case-baseline petition events:

| Claim | Resolves against |
| --- | --- |
| Disposition (`disposition`) | `Outcome.actual_granted` — the declared form is the binary grant projection; the multi-class form waits on a per-label distribution no schema field carries |
| The petition is distributed at least once more (`relist-increment`) | `Outcome.signals.distribution_count` past `Prediction.context.distribution_count` |
| The Court calls for the Solicitor General's views (`cvsg-increment`) | `Outcome.signals.cvsg_date` becoming non-null, from null (and observable) at prediction |
| The grant disposes in the cert order (`summary-disposition-route`) | `Outcome.disposition_route` — a GVR or a judgment riding the grant order, against a grant set down for plenary review; masked on every non-grant |
| Some Justice notes a dissent from the denial (`dissent-from-denial`) | `Outcome.noted_dissent_from_denial` — aggregated existence read from the order text, never which Justice; masked on every disposition that is not a denial |

The two increments are the ones whose signals are already populated:
`distribution_count` is set on every live SCOTUS row and `cvsg_date` on the
petitions that have one. A relist or a CVSG is also a genuine forward call — it
happens days after a conference distribution, which is exactly when a prediction
is committed. The two order-text markers are the opposite case: they are written
only where a disposing order's text was retained, so most committed events carry
the not-assessed null rather than a reading (*The availability mask*, below).

**Merits** — each declared merits moment is forecast against the one merits
outcome recorded (`Outcome.judgment`, resolved by judgment detection from the
docket's disposition entry):

| Claim | Resolves against |
| --- | --- |
| Judgment (`judgment-disturbed`, declared under `merits-v1`) | `Outcome.judgment` through the disturbed projection (`pipeline.judgment.judgment_disturbed`) — the declared form is binary, exactly as the cert disposition claim's is; the multi-class form waits on a per-label distribution no schema field carries |
| Each justice's vote | `Outcome.votes`, per justice — **not declared**: the merits outcome writer records no votes (docket text discloses no provenance denominator), so the resolution channel is empty by construction; see `docs/decision-model.md` |
| Majority author | *no field yet* |
| A concurrence is filed | *no field yet* |
| A dissent is filed | *no field yet* |

Disposition is **one** claim, not two. `Outcome.actual_granted` is a pure
function of `actual_disposition` (`pipeline.outcome.granted_flag`), so scoring
both would score one belief twice — see *No claim may be derived from another*.
It is also the set's one candidate for a multi-class score: the disposition
vocabulary has eight values, so its full-resolution form is the sum of
per-value Brier terms, which has the same properties as the binary rule. The
**declared** form is nonetheless binary — the grant projection — because a
multi-class claim needs a per-label distribution and no schema field carries
one; when such a field exists, the fineness preference below points at the
multi-class form. The binary form covers every declared claim.

### Semantic claims

Require matching a predicted proposition against the actual opinion text, so they
are graded by the cross-evaluator rather than computed.

| Claim | Graded against |
| --- | --- |
| The doctrinal ground of the majority | The majority opinion |
| What a concurrence splits off | The concurrence |
| The argument a dissent rests on | The dissent |

These three are the family's starting candidates, not its declared set. *The
claim vocabulary, and the tests applied* runs the eight tests below over them —
plus one the eight do not supply, which is alpha rather than pre-registered —
and records which two `semantic-v1` declares, which are deferred, and which are
rejected. Everything specific to the family lives in *The semantic family,
alpha*, deliberately quarantined from the pre-registered body of this document.

A semantic grade is formed with the predictor's name removed, because a grader
who knows whose claim it is will anchor on it, and the judge validation below —
tau-b of the grade against the mechanical record — would then partly measure the
anchor instead of the claim. The qualifier is load-bearing and is stated with
the claim rather than after it: what the harness removes is the *name*, and
two identifying channels stay open by design — prose style, and the staged
transcript's call-class profile (its tool names are respelled as neutral
classes; their shape survives). Both are set out below.

## The scoring rule

The claim set is **fixed and mandatory**: the harness declares, per declared
moment (with an event-kind fallback for events outside the moment table —
entry-pinned events and legacy ids), exactly which claims a prediction
carries, and a predictor states a probability for every one of them. It cannot add claims and it cannot skip them. *Why the set
is mandatory* explains why that is not the obvious design and is nonetheless the
right one.

For a claim with predicted probability `p`, outcome `y` in {0,1}, and a
harness-computed baseline `b`:

```
score = (b - y)^2 - (p - y)^2
```

the Brier score of the baseline minus the Brier score of the forecast. The claim
set's score is the **sum** over its claims.

`b` is the harness's, never the predictor's. A predictor that supplied its own
baseline would maximize trivially by declaring one far from the outcome — at
`b = 0` against `y = 1`, a full point per claim. So `b` is computed from history
under the same strictly-prior-Term guard `segment_base_rate` uses, pinned before
the outcome exists, and stamped into the evaluation like `usage.json` and the
process version: a harness field, not an agent's word.

A multi-class disposition claim would take the sum of per-value Brier terms,
which has the same properties; the declared disposition claim is binary (see
*Mechanical claims*), so today every claim takes the binary form.

### What the rule does and does not protect against

Three properties hold exactly, and one hoped-for property does not.

**Reporting the baseline scores exactly zero.** Set `p = b` and the score is 0
for *either* outcome — realized, not merely in expectation. Restating the
baseline is worth precisely nothing, which is what it is worth.

**Honest reporting is optimal.** For a fixed `b`, the score differs from
`-(p - y)^2` by a term that depends on `b` and `y` but **not on `p`**, so nothing
a predictor does to `p` can move it. Expected score is therefore maximized by
reporting the probability the predictor actually holds. (Not an affine transform
in the usual sense — the added term varies with `y` — but the `p`-independence is
what propriety needs, and it is exact.)

**A confident miss costs.** The score is negative whenever the forecast sits
further from the outcome than the baseline did, so a bold wrong call is paid for.

**But volume is not penalized, and information-free volume is not worthless.**
This is the correction that matters most, and it is where the first draft of this
document was wrong.

Writing `pi` for a claim's true probability, the expectation is

```
E[score] = (pi - b)^2 - (pi - p)^2
```

Two things follow. Honest reporting (`p = pi`) earns `(pi - b)^2`, which is **at
least 0 always and strictly positive whenever the baseline is not exactly
right**. And there is no `pi` and `b` for which declining a claim beats
attempting it honestly — so attempting everything is weakly dominant, and
"declining forgoes bits" was never a real trade-off.

The consequence is sharper than it looks. A predictor with **no case-specific
information at all**, reporting only the correct long-run rate for that claim
type, collects `(pi - b)^2` per claim, every claim, forever. It grows linearly in
the size of the claim set.

That is not hypothetical here. This repo's baseline configuration pools the
last ten Terms (`salience.base_rate_lookback_terms`, matching the rendered
table's window — every walked Term today), while the per-Term
band rates span roughly 26%–48%. A predictor that reports the *recent* rate
rather than the pooled one banks about `(0.40 - 0.30)^2 = 0.01` a claim, knowing
nothing about the case. Where `b` is estimated from `n` prior observations at
all, the free expectation is about `pi(1-pi)/n`.

So a positive claim total is **not** evidence of case-level skill.

### The floor, which is not optional

Because information-free volume pays, a claim total is unreadable alone. It
travels with a **floor** and the **lift** over it, exactly as an accuracy figure
travels with the always-deny floor:

- the **floor** is the realized total of the control conditioned the way the
  predictor is conditioned: it reports, for every scored claim, the harness
  baseline itself. That control's total is identically zero — restating the
  baseline is worth exactly nothing, by propriety — and the zero is *computed*
  per block rather than asserted, so the definition and the published number
  cannot drift apart. Test 4 below is why the control is the conditioned one:
  any computable nonzero control (a recent-window rate, an unconditional rate)
  measures window drift or a conditioning mismatch rather than
  information-free score, and can sit below zero in expectation — the failure
  *The floor priced none of it* records.
- the **lift** is the predictor's total minus that floor — identical to the
  total while the floor is identically zero.

What the floor prices, then, is exactly baseline-restating and no more. The
information-free score that remains unpriced is the expectation from base-rate
drift — the `(b − pi)²` worked example above, about 0.01 a claim where per-Term
rates move as these do, and the dominant term — plus baseline estimation
error, about `pi(1−pi)/n`, small at the pooled denominators. So neither the
total nor the lift is evidence of case-level skill on its own, and neither is
a rank key: the comparison that carries a skill claim is head-to-head at equal
coverage, which cancels the baseline term entirely (*Why the difference form*,
below). Publishing the total without the floor beside it would still repeat,
on a new surface, the mistake `metrics/README.md` already forbids for accuracy
— the floor's presence is what states, in the artifact itself, which control
was priced.

Two supporting requirements: each claim's baseline needs a stated minimum
observation count and a smoothing rule, since the unpriced free expectation is
largest exactly where the history is thinnest; and the baseline's lookback
window has to be stated with the figure, because moving it re-bases every
claim score at once and a comparison across the change is not a comparison.
The cert set lands the count on both its live baselines — the band rate pools
denominators in the weighted hundreds to thousands, and the summary-route rate
carries `SUMMARY_ROUTE_BASE_RATE_MIN_GRANTS` (30 grant-family rows pooled
strictly-prior) — while deferring the smoothing rule. The merits set is the
thin-history case and lands the same count:
`MERITS_BASE_RATE_MIN_PARSED` (30 parsed judgments pooled strictly-prior),
below which there is no baseline and the claim goes unscored. The **smoothing
rule** is deferred on every one of them, and that is the standing debt: at a
floor of 30 the unpriced baseline-estimation expectation is `π(1−π)/n ≈ 0.007`
per claim, the same order as the per-claim drift term this document already
calls dominant — so a merits claim total is read exactly as the cert one is,
never as case-level skill on its own, and a smoothing rule is owed before any
claim total resting on a floor-sized pool is published as evidence rather than
as coverage.

### Why the set is mandatory

Letting a predictor decline claims looks generous and is a trap.

Reporting `p = b` already scores identically zero, so a predictor with no view
loses nothing by saying so numerically. Declining buys it nothing the baseline
does not already give — except concealment. And it introduces two problems that a
mandatory set does not have.

**Coverage becomes a confound.** Two predictors attempting different claim sets
have incomparable totals: one that claimed only the easy half can outscore one
that took on everything and did well.

**Restricting to the shared claims does not fix it.** The intersection is itself
selected. A predictor attempts a claim when it expects to do well on it, so
attempt and error correlate by construction, and a predictor with good
*self-knowledge* — declining precisely the claims it would botch — wins every
intersection comparison without being a better forecaster over the fixed set.
That is skill at claim selection wearing forecasting's clothes. The intersection
describes the selection; it does not remove it. Worse, the intersection differs
per pair, so intersection totals are not transitive and there is no comparable
column to rank on at all.

A fixed mandatory set dissolves all of this: coverage is 100% by construction,
totals share a denominator, and the selection effect has nowhere to live.

### No claim may be derived from another

A sum over claims assumes the claims are separate bets. Where one claim is a
deterministic function of others they are not, and a single insight gets paid for
twice — with no correlation penalty, because each claim is scored independently.
Propriety does not rule this out: reporting an honest belief on both a claim and
its derivative is honest, and still double-counts.

Two live instances. `actual_granted` is a projection of `actual_disposition`
(`pipeline.outcome.granted_flag`), so they are one claim, not two. And a vote
split is a tally of the individual votes, so a predictor could re-encode "6-3" as
nine per-justice claims and multiply the same information ninefold.

So the declared set must be **non-redundant** — no claim entailed by the others —
and where a coarse and a fine claim both exist, the fine one is the claim,
because it carries more and the coarse one adds nothing.

This also fixes the weighting, which is otherwise silent and accidental: nine
per-justice claims against one disposition claim weights the vote dimension nine
to one. That ratio is a real choice about what the score measures, so the harness
declares it rather than letting the claim census decide it.

### Why the difference form, not the repo's ratio form

`pipeline.evaluate.brier_skill` uses the **ratio** `1 - brier / baseline_brier`,
and the headline metrics keep using it. Per claim the difference is the right
form:

- **The baseline cancels in a head-to-head.** On a shared claim set,
  `score_A - score_B = (pi - p_B)^2 - (pi - p_A)^2` — the baseline term drops out
  entirely. So a pairwise comparison at equal coverage is *immune* to the
  baseline error the floor above exists to bound. This is the strongest argument
  for the difference form, and it is why head-to-head is the defensible
  comparison.
- **Ratios do not compose.** Summing `1 - b1/b0` across claims is not a quantity
  with a meaning; summing Brier differences is, and a decomposition whose parts
  cannot be added is not a decomposition.
- **The ratio is unstable where the baselines live.** It is undefined when the
  baseline's Brier is zero (the implementation returns `None`), and near the
  endpoints it explodes: at the baseline band's `b = 0.009`, a `y = 0` outcome
  and `p = 0.3` give a ratio skill of about **-1110** where the difference form
  gives **-0.09**.

The two forms answer different questions, so both stay. Worth noting that the
existing code already takes *means of ratios* (`leaderboard`'s
`population_brier_skill_score`, and the cert back-test's equivalent), which inherits
that unbounded negative tail — one baseline-band cell can dominate the mean. That
is a live property of the current metrics, not something this document introduces.

### Why a sum, not a mean

Over a mandatory set the two differ only by a constant factor, so the choice is
presentational. It matters for what gets reported: a mean over *attempted* claims
would reward declining, which is one more reason the set is mandatory.

### Reading a total honestly

**It is not bits.** The motivation for decomposing an outcome is that the parts
carry far more information than a disposition label, but Brier differences are
not information and do not add as bits. The rule whose sum *is* bits over
baseline is the log-score difference; Brier is chosen instead because the log
score is unbounded as `p` approaches 0, and an agent-authored probability of zero
is a live risk rather than a theoretical one. The total is in Brier units and
should never be described as bits earned.

**It needs a denominator and a stratum.** A total accumulates over claims and
over events, so it is reported per event with the event count beside it, and it
is never pooled across the forward, retrospective, and procedural strata —
`metrics/README.md` forbids that for every other metric and nothing here is an
exception.

**One claim can be the whole total.** Extreme baselines are asymmetric: at
`b = 0.95` a `y = 1` outcome caps the earnable at 0.0025, while a `y = 0`
surprise pays up to 0.90. So a single lucky surprise can swamp dozens of honest
calls. Report the largest single-claim contribution beside the total, so a total
that is one claim in disguise is visible in the same breath.

**It is a grid.** A per-claim score table invites picking the row that came out
well. The headline is the total over the declared set; a per-claim score is
diagnostic, and a claim singled out afterwards describes that claim rather than
the predictor.

**It is not a rank key.** Its variance is unbounded above and a bold uninformed
spray has a fat right tail, so on the leaderboard's N-unweighted point estimates
variance-seeking would buy rank. Claim totals report head-to-head at equal
coverage, with the floor and the event count.

### Replay cells cannot produce a claimable total

A replay cell's case is decided and its opinion is public, so every claim in the
set is *retrievable* rather than forecastable. Each claim can earn up to about a
full Brier unit, so a contaminated replay total is the largest number this
surface can produce — an impressive figure manufactured entirely by retrieval.

Replay claim totals are iteration instruments only, and never claimable, on the
same footing as every other back-test number. **The leakage grading has yet to
reach claim level, and the gap is now live rather than pending.** It grades
outcome-revealing retrieval for *the disposition*, and that no longer covers
every claim that scores: whether a grant was a GVR or went to argument is a
distinct facet of the outcome, legible in the same order text that mints its
ground truth, so a replay cell that reads the grant order can earn a clean
disposition-scoped grade on a claim it retrieved. A scoring increment claim
widens "the outcome" the same way. Widening the grade is due with the per-Term
cuts that give the increments a baseline, and until it lands the route claim's
resolution on a replay cell is ungraded for retrieval — which is one more reason
replay totals never leave the iteration lane.

## Advisory, and segmented

Claim scores never alter `correct`, `brier_score`, `vote_accuracy`, or
`brier_skill_score`. They are a separate block, segmented the way the leakage
assessment is: they describe a cell without changing the numbers it is ranked on.

That is a starting posture, not a permanent one — but note where the process
digest actually moves, because it is not where it looks. The digest hashes the
prompt bytes and the resolved actor config, so it moves as soon as a **prompt**
asks for claims: that is the advisory step, not the folding-in step. Composing a
headline differently is a `leaderboard` / `pipeline.evaluate` /
`pipeline.base_rates` edit and moves no
digest at all. What folding-in would break is comparability with cells already
blessed under an earlier digest, which is a promotion-time decision rather than a
digest one.

## A claim set that failed

The first set proposed against this rule was the two cert-signal claims — *the
petition is relisted at least once* and *the Court calls for the Solicitor
General's views* — chosen because the corpus already carried both signals and the
outcome record could be made to freeze them. Signals being *populated* is not the
same as a claim being *resolvable*, and the difference is what the set failed on.
It is recorded here so the next set is chosen against these tests rather than
rediscovering them.

**The claim was resolved as a level, not an increment.** This is what actually
sank it. The resolver asked whether the count reached two *by resolution*, not
whether it rose past what the predictor could see. A forward cell's snapshot
carries the docket's proceedings intact, so distributions already recorded are
readable; for a petition already relisted when it is predicted, "will be relisted
at least once" is trivially true and a predictor writing `1.0` scores near the
maximum without forecasting anything. Fixing this needs the value **as at
prediction** on a committed artifact — the corpus column is mutable and
`Outcome.signals` freezes only the resolution-time value. `Prediction.context`
is that artifact now (*Why a cert-stage claim resolves against the outcome*,
below); the withdrawn set was specified before it existed, against a record
whose only prediction-time holder was the uncommitted `record/` snapshot.

**Two figures that argued the withdrawal are retracted.** The first: that
`salience_band` determines "relisted at least once" for 9,919 of 9,924 rows,
making the claim a lookup. `salience_band` is a function of `distribution_count`
and `cvsg_date` (plus a circuit nudge bounded below any cutpoint), so that
measurement compared a derived field against a predicate on *its own input, at the
same instant*. It is an identity up to the CVSG carve-out — the 5 residual rows
are exactly the petitions with a CVSG at one distribution or fewer. The band a
predictor is shown is computed from the count **as at prediction** and is silent
about whether the count will later rise.

The second: that about 37% of selected petitions already sit at two or more
distributions when predicted. Wrong on both axes. It described *selected*
petitions while claiming something about predicted ones, and only 410 of 3,516
selected rows carry a prediction at all. And it was read off each row's **final**
count rather than its count as at prediction. Since the count never falls below
its earlier value, 37% *bounds that share above* rather than estimating it — a
tight bound, because for most petitions the count has not moved since prediction,
but a bound. The honest quantity needs the provisioned snapshot re-parsed. The
underlying point survives either way: for a petition already relisted, "will be
relisted at least once" is trivially true.

Measured over the population the gate actually predicts on — paid modern-cert
petitions, live/historical slice, resolved, denial-reweighted, conditioned on
sitting at a single distribution — a petition faces about a **26%** chance of
being relisted at all (est. n≈13,100). Over the whole live-parsed slice with IFP
included the same rate is **19%** (est. n≈43,300).

The hazard is flat through the first relist and sharp after it, which is the part
worth knowing: 26.3% at one distribution (est. n≈13,100), 27.1% at two
(est. n≈3,400), 46.7% at three (est. n≈930), 71.3% at four (est. n≈440). The
first step moves under a point; the modal relisted petition sits at two. Read the
tail with its denominator — at four distributions the raw rate is 55.5% against
71.3% reweighted, so the weighting is doing most of the work there.

Both rates pool OT2017–OT2025 including any given case's own Term. That is
tolerable for a figure in a document and disqualifying for a claim baseline,
which would need the strictly-prior-Term guard `segment_base_rate` already
applies. They are also resolved-only, which understates slightly because
relisting delays resolution — under a point pooled, but roughly ten points wide
in an open Term.

Neither figure is published as such: both were computed directly over the
corpus for this document. The statpack's relist and CVSG cuts do carry the
paid-scored-segment conditioning (`row_filter=_is_scored_segment_row`), so the
population matches — but they publish terminal-bucket shares pooled across
every Term, not the per-count forward hazard, so the hazard figures here still
have no committed artifact behind them: the same maintenance hazard as a
constant in a prompt, and the per-Term hazard cut is what would retire it.

A base rate far enough from 0 to be worth forecasting leaves room for a forecast
to move it; whether the docket and the briefs support *skill* over that base rate
is unmeasured, because nothing here has ever scored a predictor on relist.

The weighting is not optional bookkeeping. The walk's legacy sampled rows keep
one denial in ten (`sample_weight` reconstructs the rest; freshly walked rows
carry weight 1), and relists correlate with non-denial, so a raw count runs high
while legacy rows remain in the pool — measured at 26.2% unweighted against
19.0% reweighted over the same rows. Worse,
the frame is not uniform: OT2025 comes from the live poller at weight 1 while
earlier Terms come from the walker, so a row-count pool silently mixes two
sampling designs. `metrics/README.md` states the rule this paragraph is obeying.

**The floor priced none of it.** The control was to report a recent-window rate
while the baseline pooled every prior Term, and the gap between the two windows
was to bound the free score. On real data that gap is under three percentage
points, so the floor came to roughly zero — and negative in expectation wherever
the pooled baseline is the better calibrated of the two. Meanwhile a predictor
knowing only the *selected* population's rate banks an order of magnitude more
than the floor charges. A floor built from a window difference measures window
drift, not information-free score.

**A published rate was censored.** The per-Term CVSG rates counted resolved
petitions only, on the reasoning that a pending petition can still draw a CVSG
and counting it would understate the rate. That is right for relists and backwards
for a CVSG, which *adds* six to twelve months to resolution — so in the open Term
most CVSG petitions are still pending and the published rate was about a third of
the true one.

### The tests a claim has to pass

Drawn from the above, and cheaper to apply than to rediscover:

1. **Is it determined by something the predictor is shown *at prediction time*?**
   Check against the provisioned snapshot and every derived field in it, not just
   the raw columns — and evaluate those fields as they stood when the cell ran,
   not as they stand now. A field that grows over a docket's life answers a
   different question at each of those moments.
2. **Is it about a change from the prediction's vantage point, or an absolute
   level?** A level the snapshot already discloses is not a forecast. If the claim
   is about an increment, the record has to carry the value *as at prediction*,
   not only as at resolution.
3. **Is its baseline conditioned on what the predictor sees?** A baseline coarser
   than the disclosed conditioning makes an uninformative claim look informative.
   A baseline conditioned on the *outcome* of the trajectory rather than its state
   at prediction is worse: it is leakage wearing a baseline's clothes.
4. **Does the floor bound the actual free score?** Not a window difference: a
   control conditioned the way the predictor is conditioned.
5. **Is the rate that feeds the baseline censored?** Ask which side of the
   observation the event sits on, and whether the open Term belongs in the pool.
6. **Is either side of the comparison derived from the other?** A field measured
   against its own input agrees with itself by construction. Name the two
   quantities and confirm neither is a function of the other — being two stored
   columns is not enough when one is a materialized function of the other — and
   confirm they are read at two different times. The reach is wider than
   agreement figures: it covers a calibration bin scored against a band-derived
   baseline, or a leakage grade computed from the parser that produced the log.
7. **Is the rate weighted the way the frame demands, and is the frame uniform?**
   The corpus's legacy denial-subsampled rows mean a raw count over the walker's
   rows overstates anything that correlates with non-denial. Pooling Terms drawn under
   different sampling designs compounds it. A reweighted rate prints `est. n=`
   and a raw one plain `n`; `metrics/README.md` is the governing statement. The
   docket pack reweights every cert cut; the statpack keeps one raw reader cut on
   purpose, so read the scope line rather than assuming.
8. **Is the baseline far enough from 0 (or 1) that a correct call is worth more
   than a season of honest reporting?** The rule pays `(b − y)² − (p − y)²` per
   claim, so at a baseline of half a percent an honest confident negative
   (`p ≈ 0`) earns `b²` ≈ 2.5×10⁻⁵ while a landed `p = 0.5` call earns ~0.74
   (a maximally bold `p = 1`, ~0.99) — a thousand quiet claims earn ~0.025
   against a single hit worth forty times that. The rule's expectation still
   punishes a spray (propriety holds at any baseline), so the failure is not
   the anti-shotgun defence giving way — it is the realized total collapsing
   to a Bernoulli draw: near a degenerate baseline the season's number is
   whichever single claim resolved positive, the *one claim can be the whole
   total* hazard above taken to its limit, and it bites exactly when totals
   are compared on point estimates. Tests 1–7 never look at the *level* of
   the baseline, only at its conditioning, so this check is separate: measure
   the realized base rate before declaring the claim, and where it is within
   rounding of 0 or 1, either aggregate the claim upward (an "any Justice
   writes" form rather than nine per-Justice forms) or leave it out. This is
   the stated exception to the fineness preference above — where the fine
   claim's base rate is within rounding of the boundary, the coarse claim is
   the claim. Dissent-from-denial notings are the worked example, and the
   declared set below is the aggregation this test forces: per-Justice, they
   appear on about one percent of petitions and concentrate in two Justices,
   so that form fails on volume; the aggregated "some Justice noted a dissent"
   form is what `cert-v2` declares. The summary-disposition route is the
   second application, aggregated along a different axis — conditioning rather
   than coarsening, since the unconditional class is what sits near the
   boundary and the grant-conditional one does not.

## What is scoreable today

**The declared cert set: `cert-v2`.** Every declared cert **moment** — the
petition baseline, the CVSG moment, the arrival moment — carries
exactly five claims, declared in `pipeline.claims` and answered in full by
every predictor (`Prediction.claims`); the harness scores them into
`Evaluation.claim_scores` at the evaluator's post-run stamp (`stamp-cell`,
beside the process version — never the evaluator's word, and an
evaluator-authored block does not survive the stamp) from committed artifacts
only: the prediction's frozen `context`, the outcome's `signals` block and the
two order-text markers beside it (`disposition_route`,
`noted_dissent_from_denial`, read against `actual_granted` and
`actual_disposition`), and the committed statpack. The same committed inputs —
statpack revision included — reproduce the same block. A claim scores only where
its outcome is disclosed **and** a strictly-prior baseline exists; each gap is
recorded on the claim's row rather than papered over, and the total sums the
scored claims alone. Two claims carry a baseline today — `disposition`, which on
this advisory surface re-expresses the headline Brier path, and
`summary-disposition-route`, which is grant-conditional and so scores on the
grants while sitting vacuously masked on the denials that are most of the
population. Everything else the block carries is committed probabilities,
banked from the first claiming cell so they are there to score once their cuts
land.

| Claim | Resolver | Baseline |
| --- | --- | --- |
| `disposition` | `Outcome.actual_granted` — the binary grant projection, restating the headline `probability` so the set is complete and self-describing (the block is advisory, so the headline Brier path is not paid twice on any ranked number); the multi-class form waits on a schema field carrying a per-label distribution | The frozen band's risk-set rate pooled over strictly-prior Terms (`prediction_base_rate`) — the same leakage-safe baseline the headline skill score uses, reused rather than duplicated, and never the terminal-band fallback, which conditions on the petition's own future |
| `relist-increment` | 1 iff `Outcome.signals.distribution_count` rose past `Prediction.context.distribution_count`; masked where either end is undisclosed | None yet. The honest baseline is the per-count risk-set hazard over strictly-prior Terms — and the hazard moves steeply in the count (≈26% at one distribution, 27% at two, 47% at three, 71% at four, denial-reweighted), so nothing coarser is properly conditioned. The pack's relist cut pools every Term, the case's own included, and its per-Term surface carries no relist cut — so the claim goes unscored until a per-Term relist-bucket cut over the scored segment lands |
| `cvsg-increment` | 1 iff `Outcome.signals.cvsg_date` is non-null, given null — and observable — at prediction; masked as **vacuous** where a CVSG already sat on the docket, there being nothing left to forecast | None yet, for the same strictly-prior gap — and the future per-Term cut must correct for the CVSG censoring recorded above, since a resolved-only rate in an open Term runs at a fraction of the true one |
| `summary-disposition-route` | 1 iff the grant disposed in the cert order — a GVR, or a judgment riding the grant order — 0 for a grant set down for briefing and argument, read **only** from `Outcome.disposition_route`. Masked as **vacuous** on every non-grant — a denial, a dismissal, a withdrawal — and as **not assessed** on any grant carrying no marker: a record with no order text, no cert-grant date, or an undated judgment entry. Never read off the `gvr` label where the marker is absent, which would make assessability depend on the answer — see below | The prior Terms' cert-order share of grants (`summary_route_base_rate`): pooled `gvr` + `summary-reversal` over pooled grant-family counts from each Term's **paid** fee-class cut — the scored population — strictly prior, above a stated minimum. Conditioned on the grant family, matching the resolver's own conditioning, and carrying one residual downward bias — see below |
| `dissent-from-denial` | 1 iff the denial's order text records any noted dissent or separate statement, from `Outcome.noted_dissent_from_denial` — **aggregated existence only**, never which Justice. Masked as **vacuous** on every disposition that is not a `denied` (a grant, a dismissal, a withdrawal — none is the Court refusing review) and as **not assessed** wherever no retained order text was read | None yet. No published section counts order-list notations at all, and the outcome field that would feed one fills only as dockets refresh — so the claim banks its probabilities, exactly as the two increments do, until a cut carries it |

**What the summary-route baseline is conditioned on, and what it still gets
wrong.** It is not unconditional: over all resolved petitions the summary class
runs near one percent, which test 8 above rejects outright, and conditioning on
the grant family is what moves it to a coin-flip-scale question. Over the
committed pack, under the configured ten-Term window that the pack's nine Terms
do not fill, the pooled prior-Term rate for a cell in OT2025 is **0.348** (278
cert-order dispositions over 799 paid grant-family rows, OT2017–OT2024 — a raw
`n`, not an estimate, because only denials were ever subsampled and every
grant-family row carries weight 1).

It reads the **paid** per-fee-class cut, not the Term-level pooled one, because
the paid class is the scored population: IFP petitions are Tier-0-excluded by
the salience gate (`docs/salience.md`), so no cell is ever an IFP row. They are
better than a quarter of the pooled grant family at roughly three-quarters GVR,
so the pooled rate reads 0.459 against the paid 0.348. Eleven points is not a
rounding error against a difference-form rule: a predictor knowing only its own
segment's rate would bank `(0.459 − 0.348)² ≈ 0.012` per scored claim, larger
than the drift term this document already calls dominant, and the
identically-zero floor prices none of it. The salience *band* needs no such cut
— the cert-order share runs 0.347 / 0.345 / 0.352 across baseline / elevated /
high — so fee class is the whole of the population gap.

Reading the fee-class cut also keeps the pooling inside what `StatPackTerm`
permits. That field warns the `dispositions` split is "safe within a Term and
meaningless between them", because the `gvr` label is a forward convention and
an un-relabelled Term carries its GVRs as plain `granted`. On the committed pack
that convention gap sits **entirely in the IFP class**, whose cert-order share
drops to zero in OT2023 and OT2024 against 0.87–0.95 in its neighbours; the paid
series stays inside 0.29–0.46 throughout.

One residual bias remains. A summary reversal is a cert-order disposition no
resolver mints — the `summary-reversal` label has none — so such an order sits
in the `granted` bucket and counts in the denominator but not the numerator,
pushing the rate down by an amount nothing the pack publishes bounds. Note what
that does and does not buy, because the tempting reading is wrong: under the
difference form a baseline that is off in *either* direction hands a predictor
reporting the true rate `(π − b)²` for free, and the floor prices none of it. A
downward-biased baseline is therefore **not** conservative and not a safety
margin; it is unearned score. The cut that would retire it is exactly the one
`Outcome.disposition_route` exists to build.

**The availability mask is a property of the record, never of the predictor.**
A claim is unresolvable — `outcome: null` on its row, excluded from the total —
only where the committed record does not disclose what it needs: an outcome
without a `signals` block, a context whose signals were unobservable, a CVSG
already on the docket making the increment vacuous. A predictor cannot decline
its way into the mask, and every declared claim is answered regardless of
whether it will resolve. `cert-v2`'s two additions widen the mask's vocabulary
by one kind: a **not-assessed** null, where the outcome's marker is absent
because no retained order text was read. A marker is written only from a payload
the refresh channel actually held, and a case's payload lives in the content
store rather than in git, so the null is the ordinary state of a committed
outcome rather than an edge — and it is exactly the state a `false` would
misreport. False and unobserved are
different facts and the record keeps them apart, the same line
`signals_observable` draws on the prediction side and `Outcome.signals`'s own
absence draws on the resolution side.

**The two additions, against the eight tests.** The same eight drawn from the
withdrawn set above, in the list's order.

*The summary-disposition route.* (1) Not determined at prediction time: the
snapshot of a pending petition carries no grant order, so nothing in it says
which route a future grant would take. (2) It is a level rather than an
increment, and legitimately so — there is no prediction-time value to move away
from, because the quantity does not exist until the grant does; the increment
discipline binds a claim about a docket field that already has a value, which
this is not. Leakage is handled structurally instead: a forward cell's docket
is pending by the provisioning guards, and a replay cell's snapshot is
truncated at its cutoff, so the claim is not keyed on `signals_observable` and
needs no context freeze. (3) The baseline is conditioned twice over on the
population that is actually scored — the grant family the resolver conditions
on, and the paid fee class the salience gate selects — and pooled strictly
prior, never on the case's own trajectory. The **sample** takes the same
discipline as the baseline, which is the subtler half: assessability is keyed on
coverage alone, so a GVR whose record carries no payload is masked exactly as an
unassessed plenary grant is. Gating only the plain-`granted` path would have
made the cases resolving 1 always assessable and the cases resolving 0
assessable only where a payload happened to be retained, and a mask correlated
with the outcome it masks is leakage wearing a coverage sentinel's clothes. What
remains is a coverage-limited population — markers are written only as dockets
refresh — which the claim's declared population states rather than corrects.
(4) The floor is the block's own: a forecaster
reporting the published prior-Term rate scores exactly 0, computed rather than
asserted. (5) Not censored on the side that matters: the rate is a ratio
*within* the resolved grant family, and a grant's route is fixed by the order
that grants it, so an open Term's still-pending petitions are absent from
numerator and denominator alike rather than from one of them. (6) Neither side
derives from the other: the marker is parsed from order text at resolution, the
baseline from prior Terms' published counts. (7) Weighting is a non-issue here
for a stateable reason — only denials were ever subsampled, so every row inside
the grant family carries weight 1 and the ratio is an unweighted count of
grants; the fee-class cut is what makes the *frame* uniform, since the pooled
cut mixes two populations of which only one is ever predicted. (8) **This is
the test the conditioning exists for.** Unconditionally the class runs near one
percent of resolved petitions, inside the band test 8 rejects; conditioned on
the grant family it is roughly a third, which is the level at which a correct
call is worth more than a season of quiet reporting. What the conditioning costs
is denominator: the claim scores only on grants, a few percent of cells in the
baseline band, so a season's realized route total rests on a handful of draws
even though its *level* clears the test. A per-claim scored count beside the
total is owed before any route total is read as evidence rather than coverage.

*The dissent from denial.* (1) Not determined at prediction time: the denial
order does not exist yet, and no pending-docket field anticipates it. (2) A
level, on the same reasoning and with the same structural leakage control as
the route claim. (3) No baseline exists yet, so test 3 is deferred rather than
passed — the claim is declared and unscored, exactly as the two increments are,
and the cut that carries it will have to condition on the denied population
that the claim's resolver masks to. (4) Same deferral: no baseline, no floor to
compute. (5) The censoring question is the reason the eventual cut cannot be a
whole-corpus rate: a noted dissent is recorded in the denial order itself, so
resolved-only is the right frame here, but the *coverage* gap is real and
separate — the marker fills only as dockets refresh, so the first cuts will
price a coverage-limited population and must say so. (6) Neither side derives
from the other. (7) Denials are exactly the rows the walker subsampled, so any
future baseline over them must be reweighted and print `est. n=`;
`metrics/README.md` governs. (8) **Aggregated existence is the whole design, and
the test is not yet passed — only survivable.** Per-Justice notings sit near one
percent of petitions and concentrate in two Justices (from the public record;
no committed cut counts them), so the fine claim fails on volume outright. The
aggregate — "some Justice noted a dissent" — is the coarsening test 8 itself
prescribes, and it *may* clear: the rate that matters is not the docket-wide one
but the rate over the **gated** population, and noted dissents concentrate in
exactly the relisted petitions the salience gate selects, so the two can differ
by a lot. Test 8's own instruction is to measure before declaring, and nothing
measures this yet — which is the second reason the claim ships with no baseline,
beside the missing cut. The `dissent_from_denial` parser over retained payloads
is what would retire the estimate, and the measurement is owed before the claim
scores rather than before it is declared.

The per-Justice prohibition is structural, not stylistic: nothing in the
mechanical family records or
resolves a per-Justice dissent, and nothing writes one into `Outcome.votes`.
`docs/decision-model.md` pre-registers that an individual cert vote is never
scored, and `pipeline.moments.scores_votes` enforces it — vote scoring is
admitted only on a declared merits moment, so a channel that populated cert
votes would not put this claim through a scored path.

**`cert-v1` is superseded where it is declared, and kept where it is the
fallback.** A version id names what a cell was *asked*, and the declaration is
resolved from the **event**, not from the prediction: `score_claims` reads
`declared_claim_set(event_id)` at stamp time and stamps the version it finds. So
the two halves of the table behave differently, deliberately. The kind-keyed
fallback in `pipeline.claims` — what an entry-pinned petition event or a legacy
id resolves to — stays at `cert-v1`, because those cells were elicited under
that contract and scoring them against a larger set would report claims they
were never asked for as unstated. Every **declared moment** advances with the
moment table.

The consequence is worth naming rather than glossing: because the set is
resolved from the event, **a moment's version bump does not re-score old cells
under the old set — it strands them.** A prediction that states only cert-v1's
three claims against a moment declaring `cert-v2` yields *no block at all*
(the set is mandatory, so a partial answer scores nothing), and `validate` names
the two unstated claims. Nothing is stranded, because no committed
prediction carries a `claims` block and the elicitation surface moved before any
`cert-v2` cell ran: the predict prompt asks for all five claims from the same
promotion that carries the declaration, which is what keeps the version bump
from being a declaration without an answer.

A claim total is likewise not comparable across the boundary: a `cert-v2` block
sums over a different set, so the two are pooled no more freely than a total
from a cell run under a different process digest — `metrics/README.md`'s
`declared_set_versions` rule is where that is enforced.

**The declared merits set: `merits-v1`.** Both declared merits moments — the
grant moment `evt-order-judgment` and the briefed moment `evt-brief-judgment` —
carry it, reached through the declared-moment table rather than by event id or
kind: a forecast taken after briefing answers the same claim as one taken at
the grant, and only the evidence behind the answer differs. The set declares
exactly one claim,
`judgment-disturbed`: the binary disturbed projection of `Outcome.judgment`,
restating the merits headline `probability` the way the cert set's
`disposition` claim restates its headline (a divergent pair voids the block
identically). Its baseline is `pipeline.base_rates.merits_base_rate` — the
statpack merits section's disturbed rate pooled over strictly-prior Terms,
version-free — read at the **grant** Term (`grant_term_year` over the merits
event's `opened_at`), never the frozen context's docket-number Term, which
runs a Term later for a summer-docketed pre-October grant and would admit the
case's own cohort; so the claim scores only
once prior grant Terms carry parsed judgments, clear the pooled minimum,
and carry the pool guard's count on every Term inside the window
(`docs/decision-model.md`'s three guards). A DIG and an equally divided
affirmance resolve 0 (undisturbed) and sit in the baseline's denominator the
same way; `docs/decision-model.md` is the registered design.

**The declared interim set: `interim-v1`.** All three interim moments — the
application on arrival, after the Court called for a response, and once one was
filed — declare the same four claims, reached through the moment table like the
merits set. The claims do not change because the forecast was taken later; only
the information set does, and that lives on the aggregation key.

| Claim | Resolver | Baseline |
| --- | --- | --- |
| `interim-disposition` | `Outcome.actual_granted` — the interim binary (relief granted), restating the headline `probability` so the set is self-describing, and voiding the block on a divergent pair exactly as its two siblings do. It reads the same committed field the cert `disposition` claim reads and reuses the same resolver; the id is distinct because baseline routing is keyed on it, and pooling the two under one id would average a cert grant rate with an interim one over populations resolving on different standards | The substantive slice's grant rate pooled over **application**-Terms strictly before the case's own (`base_rates.interim_base_rate`), read from the frozen context's Term. Version-free and band-free — an application freezes no salience band by rule, so there is nothing for the cert set's frozen-band pairing to condition on. `None` below the pooled floor, and its registered limitation travels with it: the pool is the whole substantive slice while the scored cells are reserve-selected in escalation-ladder order, so it is not conditioned as the predictor is (`docs/salience.md`) |
| `response-requested-increment` | 1 iff `Outcome.interim_signals.response_requested`, given false — and observable — at prediction; masked as **vacuous** where the Court had already called for one, the flag being max-latched so there is nothing left to forecast. The CVSG increment's shape, over the interim docket's analogue of it | None yet. The pack's `response_requested` column is an **unconditional** count over the whole substantive slice — every application that had drawn a request as at the build, pending ones included. The claim needs the arrival-conditioned hazard: among prior-Term applications that had not yet drawn one at the disclosed posture, the rate that went on to. An unconditional level fails test 3 above; and because the column's denominator is the whole slice while the resolved counts beside it are the machine-matched-resolved subset, it is also **right-censored** — a still-pending application contributes a "no" it may yet reverse — which is test 5 |
| `referral-increment` | 1 iff `Outcome.interim_signals.referred_to_court`, given false — and observable — at prediction; vacuous-masked on an application already referred, a referral never being undone | None yet, the same two gaps over `referred_to_court`: unconditional across the slice rather than the rate at which an unreferred application becomes a referred one, and censored by the same pending tail |
| `amicus-increment` | 1 iff `Outcome.interim_signals.amicus_briefs` rose strictly past `Prediction.context.amicus_briefs`; masked where either end is undisclosed, and with **no** vacuity arm — the count is unbounded above, so a docket already carrying briefs can always carry another. The relist increment's shape rather than the CVSG's | None yet, and the gap is sharper. `with_amicus` *is* published per Term, so coverage is not the problem: it counts applications carrying *at least one* brief, collapsing the conditioning variable itself to a flag while the claim is a rise past a specific count — test 3 at its sharpest — and it carries the same pending-tail censoring |

Against the eight tests, in order of what they decided here.

**Test 2** is what the set is built around — three of the
four claims are increments resolved from *both* committed ends, the frozen
context's as-at-prediction values against the outcome's `interim_signals`, which
is what the monotone signals demand. **Test 1** passes for all four: each
resolves against a quantity the provisioned snapshot discloses a state of, read
as at the cell's own moment rather than as it stands now.

**Test 3** is the register's hardest question here, and the reason three of four
baselines are `None`: no published cut is conditioned the way the predictor is,
and an unconditional share offered in its place would make an uninformative
claim look informative. It also lands, unresolved, on the *fourth*. The interim
disposition baseline pools the whole substantive slice while the cells scored
against it are reserve-selected in escalation-ladder order, so it is coarser
than the disclosed conditioning. That gap is registered in
[salience.md](salience.md) rather than corrected — the conditioned pool is a
later estimator, applied forward — and it is why an interim skill number is not
by itself evidence of forecast skill. **Test 4** is not reached: only the
disposition claim carries a baseline at all, so no floor-bearing control exists
to bound a free score against.

**Test 5** bites twice on that baseline. Its denominator is selected for
machine-matchable resolution text, and the escalation columns beside it are
right-censored by the pending tail — a second, independent reason the increment
baselines stay `None`. Both caveats travel with the number wherever it is quoted
rather than being corrected away. **Test 7** is clean on weighting — the
application stream carries no denial sampling, so every row stands for itself
and the counts are raw — but **not** on frame uniformity: parse coverage differs
sharply between application-Terms, so a pooled rate blends a Term the poller
covered fully with one it reached only in part, and that unevenness is the
leading candidate explanation for the spread between Term rates. **Test 8**
passes on the realized substantive grant rate, which runs between roughly 9% and
32% by Term —
clear of the boundary where a season's total collapses to a Bernoulli draw.
**Test 6** holds because the two ends are read at two different times from two
different channels: the resolution end is a latched corpus column frozen at
resolution, the prediction end a re-parse of the provisioned snapshot's own
entries. Neither is a function of the other.

One seam the set does not reach today. No published surface reads an
`interim-v1` block: the claim board filters to the cert stage's first moment, so
the block is computed and banked rather than reported. The elicitation is not a
seam any more — the predict prompt asks an interim cell for all four claims from
the same promotion that carries the declaration, since a prompt edit moves the
pre-registered process digest and the two had to travel together.

Two properties of the record are worth stating rather than discovering. The
response-filed moment is the one at which `response_requested` is usually
*already* true, so that cell's increment block is mostly vacuous-masked; that is
a fact about the ladder, correctly handled by the mask, not a defect in the set.
And no claim is about a response being **filed**, deliberately: a respondent may
answer uninvited, so it is not a rung of the Court's own attention; its committed
channel is a date column carrying the undated-entry undercount rather than a
max-latched flag; and the moment named for it is the one whose keep-or-drop
decision is still open — nothing in the moment register marks it provisional,
because the question is whether the moment earns its cells at all, not whether
the harness can mint it. Retiring it costs the set nothing, whereas a claim
declared on it would settle that question by inertia.

**What stays out, and why.** The merits vote and writing claims wait for a
real vote source:
`Outcome.votes` is `[]` in every committed outcome — the merits outcome
writer deliberately records none, because docket text discloses no
provenance denominator — and nothing records
authorship or separate writings for a modern case; the per-Justice forms also
fail the redundancy and volume conditions (`docs/decision-model.md` records
the full test-by-test analysis). All semantic claims wait on opinion
coverage — the operator-run channel that fills it (`fedcourts
enrich-opinions`) has landed bodies on fewer than ten rows against a
cert-granted slice of ≈1,250. Their blind-grading
precondition above is met on the explicit-identifier channel and on the
engine channel's tool names — the staged retrieval log respells them as
engine-neutral classes (`fedcourtsai.blinding.neutral_tool_class`), so the
staged *log* carries no per-engine vocabulary — though the call-class
*profile* still narrows the guessing space the way prose style does, and a
candidate's own `retrieval.md` prose can name a tool the scrub's identity
terms do not cover (the blinding module's residual list states these). The alpha
that will meet them when they land — and what it deliberately
does not yet decide — is *The semantic family, alpha*.

### Where each forecast content class goes

`predicted_reasoning.md` is a forecast document, and the whole point of keeping
it apart from `reasoning.md` is that a forecast can be scored while a rationale
cannot. Nothing scores the document itself, and nothing ever will: prose is not
a resolvable object. What is scored are the **structured** claims that carry the
same content — the mechanical `claims` block, and on a merits cell the graded
`semantic_claims` block. This register is the join between the two. Every
content class the predict prompt asks a cell to commit to appears here with its
route, so that *unscored* is a stated position rather than an oversight. A class
the prompt elicits and this table does not name is a defect in one of them.

**Context-only** is a real route, not a euphemism. It means: elicited because it
disciplines the forecast and because a reader of the cell needs it, resolved
against nothing, and never counted anywhere. Each context-only row names what it
would take to move — a field, a channel, a widened framing — or names the
pre-registered rule that keeps it there permanently.

| Stage | Content class the prompt elicits | Route | State |
| --- | --- | --- | --- |
| cert | Whether the Court grants review | `disposition` (`cert-v2`), restating the headline `probability` | **Scored** against the frozen band's risk-set rate over strictly-prior Terms, subject to the version pin — the same baseline the headline skill score uses |
| cert | Whether the petition is relisted further | `relist-increment` (`cert-v2`) | Declared and resolved; baseline pending a per-Term relist-bucket cut, so the probability is banked |
| cert | Whether a CVSG issues | `cvsg-increment` (`cert-v2`) | Declared and resolved; baseline pending a censoring-corrected per-Term cut |
| cert | *When* a CVSG would issue | Context-only | No timing claim is declared at any stage; a horizon claim needs a resolution-clock design the register does not have |
| cert | Whether a summary disposition is the likelier route | `summary-disposition-route` (`cert-v2`) | **Scored**, conditional on a grant, against the prior Terms' cert-order share of paid grants — but *not assessed* wherever the outcome retained no route marker, which is the ordinary state of a committed outcome rather than an edge |
| cert | Whether any dissent from denial is noted | `dissent-from-denial` (`cert-v2`) | Declared and resolved as aggregated existence, and *not assessed* wherever no order text was retained; baseline pending a cut over the denied population, so the probability is banked either way |
| cert | *From whom* the dissent comes | Context-only, permanently | The per-Justice form is a pre-registered prohibition (`docs/decision-model.md`): a cert vote is observed only when a Justice chooses to note it, and `moments.scores_votes` denies vote scoring off the merits stage by default |
| cert | Which question presented the Court would take | Context-only; named `semantic-v2` candidate | It resolves against the **grant order and the QP text**, not an opinion body, so declaring it needs `requires` widened past an opinion class; and pinned at the cert stage it is ~96% masked over the paid modern-cert census, since a QP is never taken in a denied case |
| interim | Whether a response will be called for | `response-requested-increment` (`interim-v1`) | Declared and resolved; baseline pending an arrival-conditioned hazard the pack does not publish |
| interim | Whether the application is referred to the full Court | `referral-increment` (`interim-v1`) | Declared and resolved; same gap |
| interim | How many further amicus briefs arrive | `amicus-increment` (`interim-v1`) | Declared and resolved; same gap, sharpened — the published column collapses the count to a flag |
| interim | How the application is disposed of | `interim-disposition` (`interim-v1`) | **Scored** above the pool's registered floor, against the strictly-prior substantive grant rate |
| interim | *When* it is disposed of | Context-only | The timing row above, on the interim docket |
| merits | Which of the six judgment labels the Court enters | `judgment-disturbed` (`merits-v1`) on the binary; the multi-class form is context-only | The binary is **scored**; the six-way form waits on a schema field carrying a per-label distribution, exactly as the cert disposition claim's does |
| merits | Whether a procedural exit (a DIG, an equally divided Court) is live | Folded into `judgment-disturbed` | Both resolve *undisturbed*, so the binary prices them; the label-level call rides the multi-class row above |
| merits | The ground the majority rests on | `majority-ground` (`semantic-v1`) | **Graded**, not scored. The machinery is live end to end; every unit masks until opinion bodies accrue, and the vantage caveat travels as prose |
| merits | How broad that ground is | `ground-breadth` (`semantic-v1`) | The same, on a separate axis — never a conjunct of the row above |
| merits | The ground stated coarsely (statutory vs constitutional, which provision) | **Rejected** | Fails test 2: the question presented already discloses it, so it is a level the snapshot hands the predictor rather than a forecast |
| merits | The vote lineup and the split | Context-only, banked in `votes` | Pre-registered pending a real vote source: `Outcome.votes` is empty on every committed outcome because docket text discloses no provenance denominator. Merits votes are banked and scored the day a channel exists; cert votes never are |
| merits | Whether a separate writing splits the rationale from the result | Context-only; **mechanical** family the day a field records it | Existence is a countable docket fact, not a reader's judgment, so it belongs with a real baseline and a proper score rather than as prose graded by impression. `semantic-v1` holds no place for it |
| merits | Which question presented the Court reaches and which it leaves | Context-only | The merits-side twin of the cert QP row, with the same framing gap |
| merits | Authorship and the writing roles | Context-only | No artifact records either; the prompt says so and tells the cell not to present them as the scoreable part |
| any | The rationale for the predictor's own number | Never scored, by construction | That is `reasoning.md`, a different document with a different epistemic status: it resolves against nothing. `reasoning_quality` grades its soundness and grades no forecast |

Three properties of the table are worth reading off it. **Every scored route is
mechanical or graded, never prose** — the document is the human-readable form of
a structured claim, and the two must agree, but only the structure resolves.
**Banked is not scored**: six declared claims carry no baseline yet — the two
cert increments, `dissent-from-denial`, and all three interim increments — and
their probabilities accumulate against cuts that do not exist rather than
counting toward anything. And **two rows are permanent**: the per-Justice cert vote and
the coarse doctrinal ground are not waiting on data — they are ruled out by a
pre-registered prohibition and by test 2 respectively, and a later version would
have to answer those reasons rather than rediscover them.

### Why a cert-stage claim resolves against the outcome, not the corpus

`distribution_count` and `cvsg_date` are also **corpus** columns, and the corpus
is mutable: there they carry the current value, not the value at any fixed
moment. Resolving a claim against them would break condition (1) — a claim needs
a source fixed before scoring — in a way that is easy to miss, because the claim
looks scoreable and the number looks right.

Two distinct problems, and only one of them is solved. Re-scoring the same cell a
month later would read a different column value, so the score is not reproducible
— which for a pre-registration record is disqualifying. Separately, an increment
claim needs the value at *both* ends: as at prediction and as at resolution.

The reproducibility half is fixed, on the outcome rather than on the scoring:
`outcome.json` carries a `signals` block recording the distribution count and the
CVSG date **as at resolution**, beside the disposition it already records. That
end is immutable and committed, so it scores the same way forever.

The other end is committed too: `Prediction.context` is the harness-written
`PredictionContext` block, derived from the provisioned snapshot — never the
agent's word — carrying `distribution_count`, `cvsg_date`, the salience band
and its version, the interim escalation trio (`response_requested`,
`referred_to_court`, `amicus_briefs`, frozen on application cells only), and
`signals_observable`, which is what keeps absence honest for both families
(a snapshot whose proceedings were never parsed reads as unobservable, not as
zero). An increment claim is therefore computable end to
end: the prediction-time value from the prediction's own context block, the
resolution-time value from the outcome's matching signals block — `signals` at
the cert stage, `interim_signals` at the interim one, on the identical argument. The block is nullable, and
**every committed prediction predates it** — the field and the harness path
are committed, no committed data yet exercises them — so an increment claim
scores only the cells that carry the block: a coverage boundary the claim's
declared population must state, not a defect, and a **time-skewed** one (the
covered cohort is whatever runs after the field landed, so a coverage-limited
total is not comparable to a full-set figure).

The `Outcome.signals` block's *presence* carries meaning too. It is written
only where the proceedings were live-parsed, mirroring the corpus's own
coverage rule, so an absent signals block means nothing was observed while a
present one means it was — and inside it a null CVSG date says no CVSG was
called for rather than that nobody looked. A claim cannot resolve against a
field that conflates those two. `Prediction.context` draws the same line
differently: the block is written on every provisioned cell, and
`signals_observable` inside it is what separates observed-absent from
never-parsed.

### What that adds up to

The merits *vote and writing* half of this document is blocked on data that is
not scheduled:
per-justice votes and opinion bodies. That is the honest state of it, and it is
why that half of the taxonomy is pre-registered rather than implemented. The
merits *judgment* half is not blocked: judgment detection resolves
`Outcome.judgment` from the docket, and `merits-v1` declares its one claim.

All three mechanical halves are declared: `Outcome.signals` and the two
order-text markers beside it freeze what a cert-stage claim resolves *against*,
`Outcome.interim_signals` does the same at the interim stage,
`Prediction.context` freezes what any of them resolves *from*, and
`cert-v2`, `interim-v1`, and `merits-v1` above are the sets the eight tests were
applied to. A change to
what a set carries is a new declaration version, never an in-place edit —
the same discipline the salience function keeps, which is why the id and the
claim count move together and a reader can price a total from the id alone.

Claim scoring still sits outside any earlier frozen process, by construction:
both prompts carry the claim contract in their digest-hashed bytes, so the
process version that asks for claims is distinct from every process that did
not, and a cell run under an earlier digest carries no claims block and scores
none. A claim total is never comparable across that boundary — the time-skewed
coverage note above is the same fact seen from the data side.

That coupling runs both ways, and it is the binding constraint on a set version
rather than a footnote to it: a declaration is only answerable once the prompt
asks for its claims, so **a set version and the prompt's statement of it move
together or the set is unelicitable**. A cert moment declaring `cert-v2` while
the predict prompt still names `cert-v1`'s three claims produces cells that
score nothing and that `validate` reports as incomplete — the declaration
standing ahead of the elicitation, which is a state to pass through in one
promotion batch, never one to run cells in. The conditional forms matter as much
as the count: `summary-disposition-route` is asked and priced **given a grant**
and `dissent-from-denial` **given a denial**, so a prompt eliciting either
unconditionally would collect a number its baseline does not answer.

Two consequences worth stating plainly:

- **Disposition alone is not worth a schema.** It would duplicate `brier_score`
  under a new name and report one claim as a "claim set". A cert-stage set of
  five, or a merits per-justice vote set, is the unit that earns the block —
  and the declared set keeps every claim whose baseline is still missing,
  because what the block collects meanwhile is their probabilities, which would
  otherwise be lost to the wait.
- **Nothing here may be published as a result** until the claims it scores
  resolve against fixed sources and the floor above is computed beside them.
  `metrics/README.md` governs what may be claimed from a number, and a claim
  total is not an exception to it.

### The mechanical↔semantic agreement, pre-registered

The semantic grader is validated against the mechanical record, not the other
way round: where a cell carries both a mechanical claim total and a semantic
grade, their association says whether the reader is measuring law or prose. So
that defining the number after grades exist cannot be a judgment call, its
definition is fixed now:

- **Estimator: Kendall tau-b** over per-cell pairs (mechanical claim total,
  semantic grade) — the same estimator the leaderboard's evaluator-agreement
  number already uses, chosen for the same reasons: it is rank-based, so
  neither scale's shape enters, and tau-b handles the ties a bounded grade
  produces.
- **Population: the intersection only.** A cell enters the pair set only where
  **both** numbers exist, and the intersection's `n` is printed beside the
  coefficient — a tau over 4 cells is a different fact from a tau over 400.
  Below an intersection of **10** cells the coefficient is suppressed and only
  the `n` is published. Cells excluded for *operational* absence — an
  evaluator cell that never ran or failed, as opposed to a record that
  discloses nothing — are counted and printed beside the intersection `n`,
  because differential cell failure on hard cases selects the pair set on
  difficulty, and a selected intersection must be visible.
- **The availability mask is a property of the record, never of the
  predictor.** A cell is excluded only where the *outcome record* does not
  disclose what a family needs (no opinion body for the semantic side, no
  disclosed level for a mechanical sub-claim) — never because a predictor
  declined or hedged. Availability selected on predictor behaviour would let
  the confident cells self-select the sample.
- **Never pooled across strata or process versions, never a rank key.** The
  pair set inherits every publishing rule a claim total already carries:
  per-stratum, per-process-version, advisory beside the board rather than
  inside it.

`metrics/claim-scores.json` (`fedcourts claim-scores`) publishes the
estimator under exactly these rules, with the evaluator's
`reasoning_quality` grade as the semantic side of each pair — the
judge-graded number the ledger already carries — pending the semantic claim
family itself, which awaits opinion coverage. That grade is formed under the
blinding bracket above, so the pair's semantic side carries no *named* anchor on
which predictor wrote the rationale; it carries the residuals the blinding
module names — the call-class profile and prose style — and
every other caveat `reasoning_quality` does. The reading contract for the
artifact is `metrics/README.md`, which is also where the rule against pooling
blinded with unblinded grades lives.

## The semantic family, alpha (`semantic-v1`)

Everything above this heading is pre-registration in the strict sense: settled
before there is data to fit it to, and changed only by a new declaration
version. **This section is not.** `semantic-v1` is an **alpha** methodology for
grading a predicted rationale against what the Court actually wrote, together
with the first claim set declared under it — laid out and wired now so that
iteration is fast when opinion text reaches coverage, provisional, unproven
against a single real opinion, and expected to change once one is seen.

**What "alpha" means here, and what it does not.** Both prompts ask
for it — a merits cell for the two propositions, a grader for the grades — so
the elicitation and the grading protocol are **inside the frozen process
digest**: the digest is the prompt bytes plus the resolved actor config, and
both prompts carry this section's contract in theirs. The label is not a claim
about whether anything asks. It is a claim about whether the design has been
tested against the thing it grades, and it has not: no opinion body is ingested,
both declared claims require a majority opinion, so every unit masks and the
methodology has never met a single real opinion.

**The set id and the process label answer different questions, and turning the
elicitation on is the second one's business.** A *set* version names what was
asked; the *process* version names who asked it and how. Eliciting a declared
set changes nothing about which claims it carries, so it takes a coordinated
re-bless of the process label and its reviews (`docs/process-version.md`; the
freeze record in [milestones.md](milestones.md) names it among the changes
riding that promotion) and **not** a new set id — which would fragment a census
across two identical declarations and spend the version vocabulary on a change
that is not one.

Three facts keep the label honest rather than a loophole.

- **No published number depends on it.** Every unit masks, so the census is
  empty and conditionally withheld; nothing in the leaderboard, the ops
  dashboard, or any committed metrics artifact reads a semantic grade. But note
  exactly what that rests on — the **absence of opinion text**, not the absence
  of an elicitation. Cells produce blocks now, so the day coverage lands they
  produce grades under this methodology with no further edit. That is the
  standing obligation the label carries: the first real grades will arrive under
  a design nobody has validated, and the inter-grader agreement number beside
  them is what says whether it held.
- **It takes nothing back.** Nothing here relaxes, restates, or reinterprets
  the mechanical family's contract — not the scoring rule, not the mandatory
  set, not the floor, not the availability mask, not the publishing rules a
  claim total travels under. Where anything in this section appears to conflict
  with a rule above it, the rule above governs and this one is wrong.
- **Supersession is the plan, not the exception.** The set that has actually
  met opinion text arrives as a new version with its own review; `semantic-v1`
  is never edited into it, and a claim added, dropped, or re-axed is a version
  bump. That bump now moves both prompts and therefore the process digest, so a
  semantic supersession is a coordinated re-bless rather than a free edit. The
  cost is real and it is the price of eliciting at all: the family bought the
  ability to accumulate blocks before opinion text exists, and paid for it in
  how expensive its next revision is.

### What a semantic claim is, and how it differs

A mechanical claim resolves in code, with no reader and no latitude. A semantic
claim resolves by a **reader** matching a predicted proposition against what
the Court wrote. Of the three conditions in *What a claim is*, one binds
differently and two do not hold at all:

1. **Resolves true or false from a fixed source.** A semantic claim does not
   resolve to a bit at all; it earns an ordinal **grade**. And its source is
   fixed only once an opinion body is ingested and content-addressed — which is
   the family's binding blocker, not a detail.
2. **Carries the predictor's probability.** It does not. `SemanticClaim`
   carries a proposition and no number, deliberately; see the next subsection.
3. **Has a harness-computed baseline.** It has none, and the family does not
   pretend otherwise.

So the unit is a **declared proposition, graded** — not a declared probability,
scored. `Prediction.semantic_claims` carries the propositions and
`Evaluation.semantic_grades` one grader's grades of them, on merits cells and
nowhere else; both are null on every artifact written before the prompts asked
for them, and on every stage that declares no semantic set.

One difference is worth stating on its own, because it inverts a rule the
mechanical family relies on. `Evaluation.claim_scores` is the **harness's**
word — an evaluator-authored block does not survive the stamp. A semantic grade
cannot be: needing a reader is the definition of the family. That is exactly
why inter-grader agreement below is mandatory rather than diagnostic.

### Why a semantic grade is not run through the scoring rule

This is the load-bearing decision of the family, and it is a refusal.

`claim_score = (b − y)² − (p − y)²` needs a harness-computed `b` drawn from
strictly-prior history, and the whole of the rule's defence rests on where `b`
comes from. A proposition like *the majority rests on textualist grounds* has
no such frequency. Every route to manufacturing one fails, and fails in a way
this document has already recorded:

- **Ask the predictor.** The rule's own text forbids it — a predictor supplying
  its baseline maximizes trivially by declaring one far from the outcome.
- **Ask the grader.** The same defect wearing a robe. The grader is a reader
  with latitude, so the number would be the reader's rather than the record's,
  and the score would inherit every bias the agreement number exists to detect.
- **Count how often past majorities rested on that ground.** There is no such
  tally, and building one means a doctrinal coding of every prior opinion —
  a harder problem than the one being scored, and one whose coding is itself a
  reader's judgment. It would also be conditioned on nothing the predictor was
  shown, which is test 3.
- **Assert an uninformative `b = 0.5`.** Asserting a baseline is not computing
  one. The free-score expectation `(π − b)²` would then be an artifact of the
  assertion, and the floor would price none of it — exactly the failure *The
  floor priced none of it* records.

So the family does not score. A semantic grade is **never** run through `claim_score`,
never enters a `total`, `floor`, or `lift`, is never summed or pooled with a
mechanical claim total, and is never a rank key. Grades are reported
descriptively, with inter-grader agreement beside them.

Whether **any** baseline is ever derivable is left open as an **empirical
question for when text exists**. A doctrinal-ground tally over ingested
opinions might support a properly-conditioned prior; it might not. Nobody here
has read a single opinion from this corpus, so settling it now — in either
direction — would be settling it from no evidence.

### The grade vocabulary

Four values, three of them ordinal (`SemanticSupport`):

| Grade | Meaning |
| --- | --- |
| `supported` | The opinion states the predicted proposition or plainly entails it |
| `partially-supported` | Right direction, wrong scope or wrong reason; or one conjunct of a compound proposition holds and another does not |
| `unsupported` | The opinion addresses the claim's axis and the proposition is not borne out — including where the opinion says the opposite |
| `not-addressed` | **The availability mask.** The record does not put the claim in question |

Small on purpose. The grade is a reader's, so every level the vocabulary adds
is a level graders can disagree on, and agreement is the number this family is
judged by. Contradiction therefore folds into `unsupported` rather than taking
a fourth ordinal level: separating *the opinion does not bear this out* from
*the opinion says the opposite* costs agreement to buy a distinction nothing
scores. A later version that finds graders agree easily may split it.

**`not-addressed` is an availability mask and a property of the record, never
of the predictor** — the same *treatment* the mechanical family gives a vacuous
claim, though not the same provenance: a mechanical mask is harness-computed
with no latitude, and this one is a reader's call, which is why a split on it
has to be counted separately at all. It bites three ways, all of them facts
about the record: no opinion body of the required kind exists (no concurrence
was filed), none is ingested, or the opinion is silent on the claim's axis. The
third is a fact about the record only because the claim's **axis is fixed by
the declaration** rather than by the predictor's free-text proposition — that
is the load-bearing reason nothing a predictor writes can move a claim into the
mask, and the declaration carries it: every declared claim states an `axis` and
a `requires` (*The declared set*), so the first and third modes are stated by
the declaration rather than left to convention. The check itself is the
grader's — nothing in the harness reads either string, and `graded_units`
matches a row by its claim id alone. It has **no position
on the ordinal scale**: counted apart, never
averaged with the ordinal levels, never inside a share's denominator, and never
inside the agreement coefficient. A masked claim never reads as one the
predictor got wrong.

### The claim vocabulary, and the tests applied

*Semantic claims* above names three candidates. This section refines them and
adds the ones the tests reject, because a vocabulary is defined as much by what
it excludes. Two survive and are declared as `semantic-v1` (*The declared set*,
below); the rest are deferred or rejected, each with its reason, so that a later
version readmitting one has to answer the reason rather than rediscover it.

First, how the pre-registered eight apply to a claim with no baseline. They
leave a gap the family has to fill itself, named at the end of this list.

Tests **1 and 2** — is it determined by what the predictor was shown, is it a
change or a level — apply directly and unchanged.

Test **6** applies directly too, but as a **protocol constraint** rather than a
filter: it rejects no candidate below and instead fixes how any of them must be
graded (against the opinion text, never against a pipeline-produced summary of
it — a grade computed from the same machinery the prediction passed through
agrees with itself by construction).

Test **3 splits.** Its "is the baseline conditioned on what the predictor sees"
half needs a baseline and is dormant. Its "is it conditioned on the *outcome*"
half — leakage wearing a baseline's clothes — applies with full force to the
**graded population** instead of to a baseline, and it is what rejects both
compound candidates below.

Tests **4, 5, and 7** are wholly *baseline* tests: the floor, censoring, and
weighting. **A semantic claim cannot satisfy them at all, because the family
computes no baseline** — there is nothing for them to be about. That is not three failing
grades so much as the reason grades stay descriptive: they go live the day a
baseline is proposed, and a proposed baseline that has not passed all of them
(and test 3's dormant half) is not a baseline.

Test **8** bites now. It asks whether a claim's realized base rate sits far
enough from 0 or 1 to be worth making — a question about the world, measurable
without adopting any baseline — and it rejects a candidate below.

And the family needs **one test the eight do not supply**, because they were
written for claims resolved in code. Call it the **gradeability** test: *does
this claim's shape degrade inter-grader agreement for reasons unrelated to the
prediction?* Agreement is the family's only check on grader latitude, so a
claim that injects noise into it does not merely score badly — it damages the
instrument every other claim is read through. It rejects the last candidate
below, and it is the one test specific to reader-resolved claims.

**It is alpha, and it is not appended to the eight.** The eight above are
pre-registered; gradeability is part of `semantic-v1` and carries that
section's status, not this one's. There is no "test 9" to cite as
pre-registered, and there will not be one until a version that has met opinion
text proposes it as such.

| Candidate | Verdict |
| --- | --- |
| The doctrinal ground of the majority, **fine-grained** | **Declared** as `majority-ground` |
| The breadth of the majority's stated ground | **Declared** as `ground-breadth` — a separate claim, never a conjunct of the one above |
| The doctrinal ground of the majority, **coarse** | Fails test 2 — a level the question presented already discloses |
| The form the question presented is taken in | **Deferred** to a `semantic-v2` candidate — resolves against the grant order, not an opinion body |
| Whether a separate writing is filed | **Deferred** to the mechanical family — a countable docket fact, the day a field records it |
| What a concurrence splits off | **Rejected** — compound, and its graded population conditioned on the outcome (test 3) |
| The argument a dissent rests on | **Rejected** — the same, for the same reason |
| The specific authority the majority relies on | Fails test 8 — a base rate within rounding of zero |
| The argument the Court declines to reach | **Excluded** — fails gradeability: an unbounded-search negative |

**The majority's doctrinal ground, fine-grained — declared as
`majority-ground`.** Which of two
rival readings of the provision carries the holding; which precedent is
extended, confined, or overruled; whether the holding turns on the canon the
petitioner pressed or the one the respondent did. Test 1: no snapshot field
discloses the Court's reasoning, so a forward cell is genuinely forecasting.

That pass is **conditional on when the cell runs**, and nothing in the
declaration records the vantage. The merits event opens at the grant, but
nothing pins a
merits predict cell to that moment, and a forward cell may retrieve without
restriction — so a cell running after oral argument can read a transcript in
which the doctrinal ground is frequently telegraphed. The claim's
forecastability decays monotonically across the Term. It does not fail test 1,
which keys on the snapshot; it is a **caveat the declared claim carries**: a
summary publishing `majority-ground` owes the prediction's date relative to
argument beside every grade, and that is unbuilt — no artifact in this project
records an argument date, so the caveat travels as prose and not as a column.
Read a `majority-ground` census as an upper bound on forecasting skill until it
does.

Test 6 is the protocol constraint, not a filter: the grade must be formed
against the **opinion text itself**, never against a harness-produced summary
of it, because grading a prediction against a summary this pipeline generated
is a quantity measured against its own input.

The replay caveat is sharper here than for a mechanical claim. A replay cell's
opinion is public, so *every* semantic claim is retrievable rather than
forecastable — and where a mechanical claim's contamination is bounded by the
increment over a baseline, a grade has no baseline to subtract, so the whole of
it is retrievable. Replay semantic grades are iteration instruments only and
never claimable; *Replay cells cannot produce a claimable total* applies in
full.

**The same ground, coarsely — fails test 2.** The question presented already
discloses whether the case is statutory or constitutional and names the
provision at issue. "The Court will interpret the statute's text" is a level
the snapshot hands the predictor, not a forecast, and a grader matching it
against the opinion would find it trivially borne out. This is what forces the
fineness above: the discriminating content is which reading, which precedent,
which canon — never which branch of law.

**The breadth of that ground — declared as `ground-breadth`, and separately.**
Whether the majority decides narrowly, on the facts or the party before it, or
announces a categorical rule reaching past them. It is a different axis from
`majority-ground`, not a finer grain of it: a predictor can name the right
doctrinal basis and be wrong about how far the Court takes it, and the reverse
happens just as often. Test 2 passes for the same reason the fine-grained
ground does — the question presented fixes what is asked, never how widely it is
answered.

They are **two claims and not one conjunct** because bundling them reintroduces
exactly the compound failure that rejects the two candidates below. "The
majority will confine *[precedent]* on narrow, fact-bound grounds" is two
propositions wearing one grade: right ground and wrong breadth collapses onto
`partially-supported` with no record of which half held, the census loses the
ability to say which axis a predictor is good at, and graders divide on how to
weigh a half — noise straight into the one figure that checks their latitude.
Split, each grade means one thing, and a reader who wants the joint claim can
read the two censuses together.

**The form the question presented is taken in — deferred to a `semantic-v2`
candidate.** Whether the Court takes the QP as presented, rewrites it, limits
it to one of several questions, or adds one of its own. It is a genuine
forecast that the snapshot does not disclose, and it survives the compound and
gradeability tests — but it does not belong in this set, for two reasons that
are structural rather than doubts about the claim. It resolves against **the
grant order and the QP text**, not against an opinion body, so it does not fit
the framing every claim here shares: `requires` names an opinion class, and a
claim graded off an order needs that framing widened before it can be declared
at all. And its natural moment is the **cert** stage, where it would sit on
petition events that mostly deny, since a QP is never taken in a denied case.
Over the paid modern-cert census that is roughly 96% masked (plenary grants
only as the numerator — a GVR takes no question presented); over the
salience-selected slice cells are actually minted on, whose per-Term grant rates
run far higher (`docs/salience.md`), it is smaller but still the majority. Either
denominator gives a census dominated by the mask rather than by grades. A version
that widens the framing and pins the claim to the
granted slice can declare it; `semantic-v1` does not.

**Whether a separate writing is filed — deferred to the mechanical family.**
Existence is a mechanical fact, not a semantic one: a filing is a docket event,
and the day a field records it the claim belongs in the mechanical family,
where it gets a real baseline and a proper score. Grading it as prose would
score a countable fact by a reader's impression. No field records it today,
which is why it is deferred rather than declared anywhere — but it is not a
semantic claim waiting for a semantic version, and `semantic-v1` does not hold
a place for it.

**A concurrence's split, and a dissent's ground — rejected in their compound
form.** Each bundles the *existence* claim just deferred (a concurrence is
filed) with a *content* claim (what it splits off on). Two problems, and the
second is the serious one.

The compound claim *entails* the existence claim, which *No claim may be derived
from another* forbids — so even once a field records the filing, the bundled
form is not admissible.

The content half is conditional on the existence half, and the conditioning is
on the **outcome** — test 3's live half, applied to the graded population
rather than to a baseline. Graded as one claim, the content is assessed only where the
document actually appeared — so a predictor that forecasts a concurrence
everywhere is graded only on the cases where it was right, and its misses
vanish into the mask. The mask discipline is not what fails here: "no
concurrence was filed" genuinely *is* a property of the record, which is what
makes this hard to see. The mask is honest about the record and silent about
the miss, and silence about the miss is the whole problem. The fix is to split
the claim — existence as a mechanical claim once a field exists, content graded
over the cases where the document exists, with the conditioning stated and the
conditional population's `n` published beside every grade. Whether the
conditional grade then carries a claim at all is one of the things a later
version has to settle with text in hand; neither half is in `semantic-v1`.

**The specific authority the majority relies on — fails test 8.** "The majority
will rely on *[named case]*." The rate at which any one named case is relied on
is within rounding of zero, which is what test 8 exists to catch. In the
family's own terms — no score, so no Bernoulli-collapsing total to point at —
the failure shows up as a **census that is almost entirely `unsupported` with
no power to discriminate between predictors**, and an agreement coefficient
driven undefined by ties, since graders agreeing that nearly everything is
unsupported produces no variation to correlate. Test 8's own remedy applies:
aggregate upward. "The holding rests on the *[named line of cases]*" may pass
where the per-case form cannot.

**The argument the Court declines to reach — excluded, on
gradeability.** A negative claim about a long text. Establishing absence means
searching the whole opinion, and absence-of-evidence in a fifty-page opinion is
a search problem rather than a reading one; two graders will disagree at a rate
driven by how hard each looked. That noise lands directly in the agreement
number, where it is indistinguishable from genuine grader latitude — so a claim
of this shape does not merely score badly, it degrades the instrument every
other claim is read through. A later version could readmit it only under a
bounded search: a named section, or a specific argument as briefed, so that
absence is checkable rather than merely unfound.

### The declared set (`semantic-v1`)

Two claims, on the **merits** moments — every declared one, since they all
forecast the same judgment and a later forecast answers the same claims off a
larger information set. No other event declares a semantic set: these are claims
about a merits opinion, and only a merits moment forecasts one.

| Claim | Axis | Requires |
| --- | --- | --- |
| `majority-ground` | The doctrinal basis the majority gives for the judgment: which of the rival readings of the provision carries the holding, which precedent is extended, confined, or overruled, and which canon the holding turns on | A majority opinion |
| `ground-breadth` | The breadth of the majority's stated ground: narrow to the facts or the party before the Court, against a categorical rule reaching beyond them | A majority opinion |

A declared claim carries an **axis** and a **requires**, and neither is
decoration. The axis is the proposition-space the claim occupies, and it is what
makes the third mask mode — "the opinion is silent on the claim's axis" — a fact
about the record rather than about whatever proposition a predictor happened to
write: fix the axis in the declaration and nothing a predictor writes can move
its own claim into the mask. `requires` names the document class the claim needs
to be gradeable at all, which is the mask's first mode. Both `semantic-v1`
claims require a majority opinion, so both are masked on every case that has not
reached judgment, and — until opinion coverage lands — on every case that has.

Everything downstream keys on the claim **id** alone: a grade's row, a graded
unit, the census. The axis constrains what a declaration *means* and what a
grader may mask, never what a grade is matched by, so it enters no join.

The set is **mandatory** in the same sense the mechanical sets are, and enforced
on both sides. `graded_units` reads the declaration first, refuses a block
stamped with another declaration rather than relabelling it, drops a block that
skips a declared claim, and ignores rows outside the set — silently, which is
right for a consumer and wrong for a record, so `validate` says the same refusals
out loud (`evaluation_semantic_grades_gradeable`) while the cell can still be
fixed. The predictor side has no consumer to refuse it at all, so `validate` is
the whole of its enforcement: `prediction_semantic_claims_conform` fails a block
that states a claim twice, skips a declared one, or names an id the declaration
does not carry.

### The grading protocol

- **Blind by construction.** The blinding requirement above is a
  **precondition** on this family, inherited unchanged: no grade is published
  from a pass that could see whose prediction it was grading, because a grader
  who knows anchors, and the agreement number would then partly measure the
  anchor. The harness delivers it through the blinding bracket, with the
  residuals its module names; a semantic grade inherits those residuals as
  published caveats, not as license.
- **One grade per declared claim, and every declared claim graded.** The set is
  mandatory exactly as the mechanical set is, for the same reason: a grader who
  may skip claims selects the graded population. A grader that finds the record
  settles nothing writes `not-addressed`; it does not skip the row.
- **The mask is the record's, three ways.** No opinion body of the required
  kind exists; none is ingested; the opinion is silent on the claim's axis.
  Never "the prediction was vague" — a vague proposition is graded, and graded
  poorly.
- **A grader must not reward paraphrase of the prediction back at itself.** The
  failure mode is a predicted proposition that restates the question presented,
  the syllabus, or the standard of review, and is therefore "matched" in the
  opinion trivially. A grade is earned by a proposition's **discriminating**
  content — what it asserted that a competent reader of the pre-decision record
  could have asserted otherwise. A proposition whose content is entailed by the
  question presented is not `supported` however cleanly it matches, because it
  was never at issue. The grade's `basis` field is the enforcement surface: it
  records what *in the opinion* the grade rests on, so a basis that restates
  the prediction rather than quoting the Court is visible on review.
- **Grade against the text, never against a summary of it.** Test 6 again: a
  pipeline-generated summary of the opinion is derived from the same machinery
  the prediction passed through, and a grade computed against it agrees with
  itself by construction.

### The agreement requirement

Because a semantic grade is the grader's word by construction, inter-grader
agreement is not a diagnostic here — it is the family's **only** check on
grader latitude, and it is what makes a grade a measurement rather than one
reader's opinion. Three evaluators grade each cell, so it is measurable.

- **Estimator: Kendall tau-b, leave-one-out**, per grader, over the
  `(case, event, predictor, claim)` units that grader shares with at least one
  peer — the same estimator and the same leave-one-out shape as
  `Leaderboard.evaluator_agreement`, reusing its `kendall_tau_b` rather than
  duplicating it, over a different population and **never the same figure** (a
  grader can track the panel on case stakes and not on grades). Rank-based, so
  the spacing of the ordinal scale drops out of the grader's *own* ordering;
  tau-b is what handles the heavy ties a four-value vocabulary produces.
  Leave-one-out because a panel mean containing the grader correlates it partly
  with itself — on a three-judge panel, by a third. Equal spacing between the
  three levels does survive as an assumption of the **peer mean**, which
  averages 0/1/2: peers `{unsupported, supported}` and peers
  `{partial, partial}` both read 1.0 and tie. A four-value vocabulary keeps
  that mild, and it is the same construction the leaderboard's number already
  uses, but it is an assumption and not a property.
- **Never published alone, and a null coefficient is never a pass.** No count
  or share is published without the agreement figure for the same cell set
  beside it, and a null figure is not one. The coefficient is null three ways —
  withheld below the threshold, no comparison to make, and **undefined for want
  of variation** — and all three bar publication.
  The third is the one worth spelling out, because it is easy to misread as
  unanimity. Tau-b is undefined when one axis is **constant across units**, not
  when the graders agree: a panel that agrees on grades that *differ* from unit
  to unit reads +1. A constant axis means either a record so uniform that every
  unit graded alike, or a **uniformly generous grader** whose own axis never
  moves — and the coefficient cannot tell those apart. The second is precisely
  the pathology this number exists to catch, so reading an undefined
  coefficient as agreement would disarm the family's only check at the one
  moment it is firing. The record separates *withheld* from *undefined*, which
  are different things to fix — a thin sample against a degenerate one — but
  neither is a licence to publish.
- **Pooled across claims, deliberately — and the pooling count travels with
  it.** The coefficient is one number per grader over every claim's units,
  because per-claim unit counts are far too thin to correlate separately. The
  cost is a Simpson-shaped reversal, and it is the *expected* shape once a set
  mixes claims of differing difficulty: a stable between-claim contrast — this
  claim type is easy, that one is hard — can carry a tau-b near +1 while
  within-claim agreement is exactly zero. A caveat in prose does not bound
  that, so the **number of claims pooled** publishes beside the coefficient,
  the way `pair_events` publishes beside `pairs` and a reweighted denominator
  prints `est. n=`. At one claim the contrast is unavailable and cannot be
  doing the work; the higher it runs, the more of the coefficient it could be.
  Splitting the coefficient per claim is a job for a version with the per-claim
  sample to spend on it.
- **A property of the panel, not of one judge.** With three graders a single
  dissenter sits inside both peers' comparison and can turn all three negative,
  so a low figure locates a disagreement rather than assigning blame.
- **Suppressed below 10 units**, with the unit count still published. The
  threshold matches the mechanical judge validation's numerically but **not in
  its unit**: that one counts cells, this one counts `(cell, claim)` pairs, and
  a five-claim set reaches 10 units on two cells. The units of one cell share a
  prediction, an opinion, and one reading pass, so they are strongly correlated
  and the effective sample is nearer the cell count. The distinct-cell count is
  therefore published beside the unit count, and it is the one to read. The
  **pooled `overall` census** inherits the same hazard from the same arithmetic
  — it reaches the minimum on units accumulated across claims — so it publishes
  its own cell count too. A per-claim census does not need one: for a fixed
  claim, one cell contributes exactly one unit.
- **A split on the mask is excluded from the coefficient and counted.** Where
  some graders read `not-addressed` and others graded on the ordinal scale, the
  unit enters neither the ordinal census nor the coefficient — it is counted on
  its own row. Those graders disagree about what the *record* discloses, which
  measures the record's adequacy rather than the predictor or the panel, and
  burying it in the coefficient would let an inadequate record read as an
  unreliable panel. But the exclusion has a price that must be stated with the
  number rather than discovered later: the units removed are the ones graders
  disagreed on *most sharply*, so the published coefficient is agreement
  **conditional on the panel unanimously agreeing the record spoke**. Read it
  against the mask-dispute count, not merely beside it — and note the exclusion
  needs unanimity on both sides, so a single mask-prone grader removes units
  from every peer's comparison.

One convention the roll-up needs and the alpha fixes provisionally: a unit graded by
several graders is counted **once**, at the panel's **lower median ordinal**, or
the census would weight a unit by its grader count — the distortion the
mechanical surface removes by deduplicating blocks to one per event. The lower
median, not the floor of the median, so the result stays on the vocabulary
(`[0, 0, 2, 2]` gives `unsupported`, never a level between two) and an even
split lands on the less supported side, so multiplicity can never manufacture
credit. Unlike the mechanical deduplication this genuinely discards information
— those copies are byte-identical, graders are not — which is admissible only
because what it discards is republished as the agreement figure. A summary
convention of the alpha.

### What this does not change

The pre-registered mechanical↔semantic agreement above pairs each cell's
mechanical claim total with the evaluator's `reasoning_quality` grade, and
`semantic-v1` **does not touch that pairing**. Whether the pair's semantic side
should become a semantic-family grade is a question for a later version to
settle explicitly, with its own review: swapping it in place would silently
redefine a pre-registered number, and a coefficient computed over two different
semantic sides is not one series.

### What remains unbuilt

The declaration and the prompts that ask for it are built — two of the three
things a grade needs. In dependency order, most binding first, what is still
owed:

1. **Opinion coverage.** Fewer than ten corpus rows carry an opinion body,
   against a cert-granted slice of ≈1,250. The channel that fills them —
   `fedcourts enrich-opinions`, operator-run over that slice
   (`docs/data-pipeline.md`) — has run, so what is missing is neither a design
   nor a dispatch but *yield*: a walk converges only the grants whose docket
   links a published cluster upstream, and re-walks the rest every run. Until
   coverage is a slice rather than a rounding error, nothing can be graded
   against text that is not there, and no amount of methodology substitutes:
   every declared claim requires a majority opinion, so every unit masks.
2. **Any baseline.** Left open as an empirical question above.
3. **An argument date.** `majority-ground`'s forecastability decays across the
   Term and no artifact records the vantage, so the caveat above travels as
   prose rather than as a column beside the grade.
4. **A counted split of the mask's grounds.** The grading protocol requires a
   grader to say in `basis` which ground it masked on — no opinion body of the
   required class, none ingested, or silence on the axis — because a missing
   document is a coverage gap somebody can fix while in-document silence is a
   fact about the Court. But `SemanticGrade.basis` is free text and
   `SemanticClaimSummary` carries one undifferentiated `not_addressed` count, so
   that distinction is readable by a person auditing a cell and by nothing else.
   While every unit masks it is the *only* signal the family produces, and the
   register's own standard — a coverage gap and a substantive finding must never
   be tradeable — says it should be counted rather than merely written down.

The prompts are built: the predict prompt asks a merits cell for one
proposition per declared claim on its declared axis, and the evaluate prompt
carries the grading protocol above — the axis discipline, the mask's grounds
and the requirement to say which one applied, and the five refusals. So is the
**mandatory-set discipline on both sides**, the discipline the mechanical family
keeps and the one place this family's enforcement had to be built rather than
inherited, since nothing consumes a predictor's block at all:
`graded_units` refuses a non-conforming grader block whole, and
`validate` holds a committed block on either side to its declaration
(`prediction_semantic_claims_conform`, `evaluation_semantic_grades_gradeable`),
so a skipped, duplicated, invented, or misversioned claim fails the cell instead
of vanishing into a census nobody can audit. That closes the hole differential
coverage across predictors would otherwise open — a pooled census reweighted
with no visible change in any denominator.

What *is* built is the whole path a grade would travel: the schema blocks, the
declaration with its axes and its lookup treating it as authoritative over any
grader's block, the descriptive roll-up with its agreement number, unit tested
against synthetic graded fixtures, and the published surface —
`fedcourts semantic-summary`, which segments by stratum, process scope, and
vantage (each stage's first declared moment, so a grant-moment forecast never
averages with a briefed-moment one), collapses re-runs to one grade per grader
per cell, and writes an artifact only where the census clears the floor *and*
some grader carries an agreement coefficient, printing the withheld state and
writing nothing below either (which is what it does today). And the
blind-grading bracket itself
(`fedcourtsai.blinding`, wired around every evaluate cell), whose alias staging
and engine-neutral tool classes remove identity from the staged bytes — with the
residuals its module docstring names, the call-class profile among them. So what
separates a declared set from a produced grade is opinion text alone — not a
shape, and no longer an elicitation.
