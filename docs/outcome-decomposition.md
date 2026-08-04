# Decomposing a predicted outcome

A binary grant/deny forecast carries at most one bit, and the base rate consumes
most of it. What a strong forecast actually delivers — the vote split, who writes,
which doctrinal ground the majority rests on, what a concurrence splits off — is
worth far more, and none of it is scored by a disposition label. This document
defines the decomposition that makes those parts scoreable, and the rule that
scores them.

**The mechanical cert-stage family and the merits judgment claim are
implemented; everything else here is
pre-registration.** The scoring rule is `pipeline.evaluate.claim_score`; the
declared sets — three cert-stage claims under `cert-v1`, and the one merits
claim (`judgment-disturbed`) under `merits-v1`, keyed on the minted merits
event — live
in `pipeline.claims`, with the resolvers, the strictly-prior baselines, and the
availability mask beside it; `Prediction.claims` carries the predictor's
probabilities and `Evaluation.claim_scores` the harness-computed block. The
first set proposed against the rule was specified in a way that did not
resolve, and *A claim set that failed* records why, in detail, because its
tests are what the declared sets were chosen against. The merits vote,
split, and writing claims and the
whole semantic family remain pre-registered only —
`docs/decision-model.md` records why the vote claims failed the tests.

The rest is pre-registration: the decomposition and the rule are settled before
there is data to fit them to, which is the only order in which the choice of rule
is credible.

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
*about* — which does not exist and is a different problem. This document
decomposes a predicted *outcome* into scoreable propositions.

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

These are the ones worth attention, because their signals are already populated:
`distribution_count` is set on every live SCOTUS row and `cvsg_date` on the
petitions that have one. A relist or a CVSG is also a genuine forward call — it
happens days after a conference distribution, which is exactly when a prediction
is committed.

**Merits** — the merits event is forecast and its outcome recorded
(`Outcome.judgment`, resolved by judgment detection from the docket's
disposition entry):

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
vocabulary has seven values, so its full-resolution form is the sum of
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

A semantic grade should be formed before the grader knows whose claim it is,
because a grader who knows will anchor — and inter-evaluator agreement, the
check on grader latitude, then partly measures the anchor instead of the claim.

Stating that as a requirement rather than a fact, because the harness cannot
currently deliver it: the evaluate contract has the evaluator read
`predictions/<predictor_id>/<run_id>/prediction.json` and write under a path
keyed on the same id, so identity is unavoidable today. The nearest existing
precedent is narrower than blinding — the evaluator forms its big-case read
before looking at the predictor's `big_case_score`, which blinds it to the
predictor's *number*, not to which predictor it is. Closing the gap needs a
harness change, and that is a precondition on scoring semantic claims, not a
detail of it.

## The scoring rule

The claim set is **fixed and mandatory**: the harness declares, per event kind,
exactly which claims a prediction carries, and a predictor states a probability
for every one of them. It cannot add claims and it cannot skip them. *Why the set
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
The cert set defers the count and the rule alike, tolerable only because its
one live baseline pools band denominators in the weighted hundreds to
thousands. The merits set is the thin-history case, and lands the count:
`MERITS_BASE_RATE_MIN_PARSED` (30 parsed judgments pooled strictly-prior),
below which there is no baseline and the claim goes unscored. It **defers the
smoothing rule**, which is the standing debt on it: at the floor the unpriced
baseline-estimation expectation is `π(1−π)/n ≈ 0.007` per claim, the same
order as the per-claim drift term this document already calls dominant — so a
merits claim total is read exactly as the cert one is, never as case-level
skill on its own, and a smoothing rule is owed before any merits claim total
is published as evidence rather than as coverage.

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
`mean_brier_skill_score`, and the cert back-test's equivalent), which inherits
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
same footing as every other back-test number. The leakage grading also has to
reach claim level before an *increment* claim scores: it grades
outcome-revealing retrieval for the disposition, which covers the one claim
that scores today, and a scoring increment claim widens what "the outcome"
means — that widening is due with the per-Term cuts that give the increments a
baseline.

## Advisory, and segmented

Claim scores never alter `correct`, `brier_score`, `vote_accuracy`, or
`brier_skill_score`. They are a separate block, segmented the way the leakage
assessment is: they describe a cell without changing the numbers it is ranked on.

That is a starting posture, not a permanent one — but note where the process
digest actually moves, because it is not where it looks. The digest hashes the
prompt bytes and the resolved actor config, so it moves as soon as a **prompt**
asks for claims: that is the advisory step, not the folding-in step. Composing a
headline differently is a `leaderboard` / `pipeline.evaluate` edit and moves no
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
   the claim. Per-Justice dissent-from-denial notings are the live example
   (from the public record, not a corpus field — nothing stored records one):
   they appear on about one percent of petitions, concentrated in two
   Justices, so the per-Justice form fails this test on volume while the
   aggregated form may pass.

## What is scoreable today

**The declared cert-stage set: `cert-v1`.** A petition-kind event carries
exactly three claims, declared in `pipeline.claims` and answered in full by
every predictor (`Prediction.claims`); the harness scores them into
`Evaluation.claim_scores` at the evaluator's post-run stamp (`stamp-cell`,
beside the process version — never the evaluator's word, and an
evaluator-authored block does not survive the stamp) from committed artifacts
only: the prediction's frozen `context`, the outcome's `signals` block, and
the committed statpack. The same committed inputs — statpack revision
included — reproduce the same block. A claim scores only where its outcome is
disclosed **and** a strictly-prior baseline exists; each gap is recorded on
the claim's row rather than papered over, and the total sums the scored
claims alone. Until the per-Term cuts below land, the one claim that scores
is `disposition` — on this advisory surface, a re-expression of the headline
Brier path — so the block's incremental content today is the committed
increment probabilities themselves, banked from the first claiming cell so
they are there to score once their baselines exist.

| Claim | Resolver | Baseline |
| --- | --- | --- |
| `disposition` | `Outcome.actual_granted` — the binary grant projection, restating the headline `probability` so the set is complete and self-describing (the block is advisory, so the headline Brier path is not paid twice on any ranked number); the multi-class form waits on a schema field carrying a per-label distribution | The frozen band's risk-set rate pooled over strictly-prior Terms (`prediction_base_rate`) — the same leakage-safe baseline the headline skill score uses, reused rather than duplicated, and never the terminal-band fallback, which conditions on the petition's own future |
| `relist-increment` | 1 iff `Outcome.signals.distribution_count` rose past `Prediction.context.distribution_count`; masked where either end is undisclosed | None yet. The honest baseline is the per-count risk-set hazard over strictly-prior Terms — and the hazard moves steeply in the count (≈26% at one distribution, 27% at two, 47% at three, 71% at four, denial-reweighted), so nothing coarser is properly conditioned. The pack's relist cut pools every Term, the case's own included, and its per-Term surface carries no relist cut — so the claim goes unscored until a per-Term relist-bucket cut over the scored segment lands |
| `cvsg-increment` | 1 iff `Outcome.signals.cvsg_date` is non-null, given null — and observable — at prediction; masked as **vacuous** where a CVSG already sat on the docket, there being nothing left to forecast | None yet, for the same strictly-prior gap — and the future per-Term cut must correct for the CVSG censoring recorded above, since a resolved-only rate in an open Term runs at a fraction of the true one |

**The availability mask is a property of the record, never of the predictor.**
A claim is unresolvable — `outcome: null` on its row, excluded from the total —
only where the committed record does not disclose what it needs: an outcome
without a `signals` block, a context whose signals were unobservable, a CVSG
already on the docket making the increment vacuous. A predictor cannot decline
its way into the mask, and every declared claim is answered regardless of
whether it will resolve.

**The declared merits set: `merits-v1`.** The minted merits event
(`evt-order-judgment` — keyed by exact event id, since its kind is `order`
and not every order event is merits) declares exactly one claim,
`judgment-disturbed`: the binary disturbed projection of `Outcome.judgment`,
restating the merits headline `probability` the way the cert set's
`disposition` claim restates its headline (a divergent pair voids the block
identically). Its baseline is `pipeline.evaluate.merits_base_rate` — the
statpack merits section's disturbed rate pooled over strictly-prior Terms,
version-free — read at the **grant** Term (`grant_term_year` over the merits
event's `opened_at`), never the frozen context's docket-number Term, which
runs a Term later for a summer-docketed pre-October grant and would admit the
case's own cohort; so the claim scores only
once prior grant Terms carry parsed judgments. A DIG and an equally divided
affirmance resolve 0 (undisturbed) and sit in the baseline's denominator the
same way; `docs/decision-model.md` is the registered design.

**What stays out, and why.** The merits vote and writing claims wait for a
real vote source:
`Outcome.votes` is `[]` in every committed outcome — the merits outcome
writer deliberately records none, because docket text discloses no
provenance denominator — and nothing records
authorship or separate writings for a modern case; the per-Justice forms also
fail the redundancy and volume conditions (`docs/decision-model.md` records
the full test-by-test analysis). All semantic claims wait on opinion
ingestion (`has_opinion` is 0 on every corpus row) and on the blinding
precondition above.

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
and its version, and `signals_observable`, which is what keeps absence honest
(a snapshot whose proceedings were never parsed reads as unobservable, not as
zero). An increment claim is therefore computable end to
end: the prediction-time value from the prediction's own context block, the
resolution-time value from `Outcome.signals`. The block is nullable, and
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

The cert-stage half is declared: `Outcome.signals` freezes what a cert-stage
claim resolves *against*, `Prediction.context` freezes what it resolves *from*,
and `cert-v1` and `merits-v1` above are the sets the eight tests were applied
to. A change to
what a set carries is a new declaration version, never an in-place edit —
the same discipline the salience function keeps.

Claim scoring still sits outside any earlier frozen process, by construction:
both prompts carry the claim contract in their digest-hashed bytes, so the
process version that asks for claims is distinct from every process that did
not, and a cell run under an earlier digest carries no claims block and scores
none. A claim total is never comparable across that boundary — the time-skewed
coverage note above is the same fact seen from the data side.

Two consequences worth stating plainly:

- **Disposition alone is not worth a schema.** It would duplicate `brier_score`
  under a new name and report one claim as a "claim set". A cert-stage set of
  three, or a merits per-justice vote set, is the unit that earns the block —
  and the declared set keeps all three even while the increments await their
  baselines, because what the block collects meanwhile is their probabilities,
  which would otherwise be lost to the wait.
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
family itself, which awaits both opinion ingestion and its blinding
precondition. The reading contract for the artifact is `metrics/README.md`.
