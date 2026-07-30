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

The rule is implementable today. Most of the *claims* are not — the corpus does
not yet carry what they resolve against, and *What is scoreable today* says
exactly which and why.

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
3. has a **baseline** probability derived from history, independent of the
   forecast.

All three are load-bearing. Without (1) a claim is rhetoric. Without (2) it
cannot be properly scored. Without (3) there is nothing to beat, and a claim that
cannot be beaten cannot earn credit.

A predictor may **decline** any claim. Declining is not an admission and carries
no penalty — see the scoring rule.

### Mechanical claims

Resolved in code against `outcome.json`. No reader, no latitude.

| Claim | Resolves against |
| --- | --- |
| Disposition | `Outcome.actual_disposition` |
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

Each claim is scored **against its own baseline**, and the claim set's score is
the **sum** of those per-claim scores.

For a claim with predicted probability `p`, outcome `y ∈ {0,1}`, and baseline
`b`:

```
score = (b - y)² - (p - y)²
```

That is the Brier score of the baseline minus the Brier score of the forecast —
the *difference* form of Brier skill. Three properties follow, and they are
exactly the three constraints the decomposition has to satisfy.

**Declining forgoes bits rather than being penalized.** A declined claim scores
0, and is excluded from any per-claim average. Silence is neutral, so a predictor
never gains by claiming something it has no view on, and never loses by admitting
it has none.

**A claim at the baseline earns nothing.** Set `p = b` and the score is exactly
0. Restating the base rate is worth precisely as much as saying nothing, which is
what it is worth. This is what stops shotgunning: a spray of claims at their base
rates sums to zero.

**Being confidently wrong costs.** The score is negative whenever the forecast is
further from the outcome than the baseline was, so volume is not free. A
predictor maximizes its total by claiming exactly what it knows and no more.

And it stays **proper**. For a fixed `b` the score is a positive affine transform
of `-(p - y)²`, so it is maximized in expectation by reporting the probability the
predictor actually believes. Because `b` comes from history and never from the
forecast, the transform cannot be gamed by moving `p`.

### Why the difference form, not the repo's ratio form

`pipeline.evaluate.brier_skill` uses the **ratio** `1 - brier / baseline_brier`,
and the headline metrics keep using it. Per claim the difference form is the right
one, for two reasons:

- **Ratios do not add up.** Summing `1 - b₁/b₀` across claims is not a quantity
  with a meaning; summing Brier differences is, and the whole point of a
  decomposition is that the parts compose.
- **The ratio degenerates at the endpoints.** It divides by the baseline's
  Brier, which is zero exactly when the baseline is 0 or 1 and matched the
  outcome — the existing implementation returns `None` there. Near the endpoints
  it is defined but explosive, and claims with near-certain baselines ("a dissent
  is filed") are common in any real claim set.

The two are not in conflict: the ratio answers "how much better than the
baseline, proportionally", for one headline number. The difference answers "how
many Brier units did this claim earn", which is what a sum needs.

### Why a sum, not a mean

A mean rewards abstention. Drop the hardest claim and the mean rises, with no
loss anywhere — precisely the wrong incentive when the point is to elicit more
bits. Under a sum, declining a hard claim moves the total by zero and the
predictor simply earns less.

### No claim may be derived from another

A sum over claims assumes the claims are separate bets. Where one claim is a
deterministic function of others, they are not, and a predictor with a single
genuine edge can bank it twice by claiming both — with no correlation penalty,
because the rule scores each claim independently.

This is a different exploit from the base-rate spray above, and the propriety
argument does not rule it out: reporting your true belief on *both* a claim and
its derivative is honest, and still collects the same insight twice.

Two live instances: `actual_granted` is a projection of `actual_disposition`, and
a vote split is a tally of the individual votes. So the claim set must be
**non-redundant** — a set in which no claim is entailed by the others. Where a
coarser and a finer claim both exist, the finer one is the claim (per-justice
votes, not the split derived from them), because it carries more bits and the
coarse one adds none.

Non-redundancy is a property of the declared claim set, not something the scoring
rule can enforce, which is why the set has to be declared and fixed rather than
assembled per prediction.

### The comparability limit, which is real

Because declining is free, two predictors can attempt **different claim sets**,
and their totals are then not comparable — a predictor that claimed only the easy
half can post a higher total than one that took on everything and did well.

So a total is comparable only at equal coverage. Reporting requires:

- the attempted and declined counts beside every total, and
- for any comparison between predictors, the per-claim scores restricted to the
  claims **both** attempted.

Publishing a bare total across predictors with unequal coverage would be a
ranking of claim selection dressed as a ranking of forecasting.

### The claim set is a grid

A scored claim set is a per-claim score table, and a table invites picking the row
that came out well. The headline is the total over a stated claim set; a
per-claim score is diagnostic. A claim singled out after the fact is a
description of that claim, not evidence about the predictor.

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

Of the eight claims above, **one** can be scored now.

| Claim | Blocked on |
| --- | --- |
| Disposition | — *scoreable now* |
| Each justice's vote | `Outcome.votes` is `[]` in every committed outcome; nothing populates it |
| Majority author, concurrence, dissent | No field on `Outcome`, and no ingestion channel supplies one |
| All semantic claims | `has_opinion` is 0 on every corpus row, so no opinion body has been ingested and the grader has nothing to read |

There is a further gap above all of these: the taxonomy describes a **merits**
prediction, and the pipeline currently produces none. Every committed event is a
petition, appeal, or motion disposition — cert-stage work. Vote splits, authorship
and concurrences are properties of a decided case on the merits, which is a class
of prediction that does not exist yet.

So this document is pre-registration, deliberately. The decomposition and the
scoring rule are settled now, before there is data to fit them to, which is the
only order in which the choice of rule is credible. `metrics/README.md` governs
what may be claimed from a number; nothing here may be published as a result
until the claims it scores can actually resolve.

Two consequences worth stating plainly:

- **Implementing mechanical scoring for disposition alone is not worth a
  schema.** It would duplicate `brier_score` under a new name and report one
  claim as a "claim set". The unit that earns the block is a per-justice vote
  set, which needs the vote data.
- **The data work is the blocker, not the design.** Per-justice votes and opinion
  text are what convert this from a document into a measurement.
