# Decomposing a predicted outcome

A binary grant/deny forecast carries at most one bit, and the base rate consumes
most of it. What a strong forecast actually delivers — the vote split, who writes,
which doctrinal ground the majority rests on, what a concurrence splits off — is
worth far more, and none of it is scored by a disposition label. This document
defines the decomposition that makes those parts scoreable, and the rule that
scores them.

**Nothing in this document is implemented.** No code scores a claim, no schema
carries one, and no prompt asks for one. It is pre-registration: the
decomposition and the rule are settled here, before there is data to fit them to,
because that is the only order in which the choice of rule is credible.

The rule is implementable today, and so are three cert-stage claims once one
field is added to the outcome record. The merits claims — vote splits, authorship,
doctrinal grounds — are blocked on data that is not scheduled. *What is scoreable
today* separates the two, because the difference is the whole plan.

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

Resolved in code, no reader and no latitude. They split by event kind, because
the pipeline predicts cert-stage events and the merits claims below describe a
decided case.

**Cert-stage** — the events that actually exist:

| Claim | Resolves against |
| --- | --- |
| Disposition | `Outcome.actual_disposition` |
| The petition is relisted at least once | `distribution_count` past its value at prediction time |
| The Court calls for the Solicitor General's views | `cvsg_date` becoming non-null |

These are the ones worth attention, because their signals are already populated:
`distribution_count` is set on every live SCOTUS row and `cvsg_date` on the
petitions that have one. A relist or a CVSG is also a genuine forward call — it
happens days after a conference distribution, which is exactly when a prediction
is committed.

**Merits** — a decided case, which the pipeline does not yet produce:

| Claim | Resolves against |
| --- | --- |
| Each justice's vote | `Outcome.votes`, per justice |
| Majority author | *no field yet* |
| A concurrence is filed | *no field yet* |
| A dissent is filed | *no field yet* |

Disposition is **one** claim, not two. `Outcome.actual_granted` is a pure
function of `actual_disposition` (`pipeline.outcome.granted_flag`), so scoring
both would score one belief twice — see *No claim may be derived from another*.
It is also the one multi-class claim here: the disposition vocabulary has seven
values, so it takes a multi-class proper score (the sum of per-value Brier terms)
rather than the binary form below. The binary form covers every other claim.

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

Disposition is the one multi-class claim; it takes the sum of per-value Brier
terms, which has the same properties. Everything else is binary.

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

That is not hypothetical here. This repo's baseline configuration pools every
prior Term (`salience.base_rate_lookback_terms` ships at `0`), while the per-Term
band rates span roughly 26%–48%. A predictor that reports the *recent* rate
rather than the pooled one banks about `(0.40 - 0.30)^2 = 0.01` a claim, knowing
nothing about the case. Where `b` is estimated from `n` prior observations at
all, the free expectation is about `pi(1-pi)/n`.

So a positive claim total is **not** evidence of case-level skill.

### The floor, which is not optional

Because information-free volume pays, a claim total is unreadable alone. It
travels with a **floor** and the **lift** over it, exactly as an accuracy figure
travels with the always-deny floor:

- the **floor** is the total earned by a control that reports, for every claim,
  the unconditional rate for that claim type over a recent window;
- the **lift** is the predictor's total minus that floor.

The lift is the number that carries a claim about skill. The raw total is
descriptive. Publishing the total without the floor beside it would repeat, on a
new surface, the mistake `metrics/README.md` already forbids for accuracy.

Two supporting requirements: each claim's baseline needs a stated minimum
observation count and a smoothing rule, since the free expectation is largest
exactly where the history is thinnest; and the baseline's lookback window has to
be stated with the figure, because moving it re-bases every claim score at once
and a comparison across the change is not a comparison.

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
reach claim level before the block is populated: it currently grades
outcome-revealing retrieval for the disposition, and a claim set widens what
"the outcome" means.

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

## What is scoreable today

Three claims can be scored on the events the pipeline actually produces. What
remains for them is a baseline apiece and the harness that computes it — not
data, and no longer a schema change.

| Claim | State |
| --- | --- |
| Disposition | Scoreable. `Outcome.actual_disposition` is committed and immutable, and `segment_base_rate` already supplies a leakage-safe baseline for the binary projection — a per-label baseline is constructible from the statpack's per-Term rates under the same strictly-prior-Term guard, but nothing builds one yet |
| Relisted at least once | Scoreable. `Outcome.signals.distribution_count` records the count as at resolution; the claim is about an increment past its value when the prediction was made |
| CVSG | Scoreable. `Outcome.signals.cvsg_date`, where a null inside the block means no CVSG rather than no record |
| Each justice's vote | `Outcome.votes` is `[]` in every committed outcome, and nothing populates it. `JudgeVote.vote` is also typed as a disposition, a vocabulary with no majority/dissent member, so a merits vote claim needs a schema change as well as data |
| Majority author, concurrence, dissent | No field on `Outcome`, and nothing on the corpus row carries authorship for a modern case |
| All semantic claims | `has_opinion` is 0 on every corpus row, so no opinion body has been ingested and the grader has nothing to read |

### Why the cert-stage claims resolve against the outcome, not the corpus

`distribution_count` and `cvsg_date` are also **corpus** columns, and the corpus
is mutable: there they carry the current value, not the value at any fixed
moment. Resolving a claim against them would break condition (1) — a claim needs
a source fixed before scoring — in a way that is easy to miss, because the claim
looks scoreable and the number looks right.

Two distinct problems. Resolving "relisted at least once" needs the value *after*
the prediction and *at* resolution, but a petition already has one distribution
when it is predicted, so the claim is about a later increment that no committed
artifact records. And re-scoring the same cell a month later would read a
different column value, so the score is not reproducible — which for a
pre-registration record is disqualifying.

The fix belongs on the outcome rather than on the scoring, and it is in place:
`outcome.json` carries a `signals` block recording the distribution count and the
CVSG date **as at resolution**, beside the disposition it already records. The
cert-stage claims now resolve against an immutable committed artifact like
everything else, so the same cell scores the same way forever.

The block's *presence* carries meaning too. It is written only where the
proceedings were live-parsed, mirroring the corpus's own coverage rule, so an
absent block means nothing was observed while a present one means it was — and
inside it a null CVSG date says no CVSG was called for rather than that nobody
looked. A claim cannot resolve against a field that conflates those two.

### What that adds up to

The merits half of this document is blocked on data that is not scheduled:
per-justice votes and opinion bodies. That is the honest state of it, and it is
why the taxonomy is pre-registered rather than implemented.

But the cert-stage half is **not** blocked on data, and no longer on the record
either: three claims, on every petition the pipeline already predicts, resolving
against committed immutable fields. What they still need is a baseline apiece,
computed by the harness under the strictly-prior-Term guard, and the floor beside
the total. That is the cheapest path to a claim set that scores something real.

Two consequences worth stating plainly:

- **Disposition alone is not worth a schema.** It would duplicate `brier_score`
  under a new name and report one claim as a "claim set". A cert-stage set of
  three, or a merits per-justice vote set, is the unit that earns the block.
- **Nothing here may be published as a result** until the claims it scores
  resolve against fixed sources and the floor above is computed beside them.
  `metrics/README.md` governs what may be claimed from a number, and a claim
  total is not an exception to it.
