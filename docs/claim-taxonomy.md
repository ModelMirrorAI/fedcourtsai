# The claim taxonomy

A binary grant/deny forecast carries at most one bit, and the base rate consumes
most of it. What a strong forecast actually delivers — the vote split, who writes,
which doctrinal ground the majority rests on, what a concurrence splits off — is
worth far more, and none of it is scored by a disposition label. This document
defines the decomposition that makes those parts scoreable, and the rule that
scores them.

It is the design half of the reasoning-scoring work. The scoring rule below is
implementable today; most of the *claims* are not, because the corpus does not
yet carry what they resolve against. *What is scoreable today* says exactly which,
and that section is the honest state of the thing.

## Naming

The two families are **mechanical** and **semantic**, after what distinguishes
them: whether resolving a claim needs a reader.

They are deliberately not called tiers. "Tier 0/1/2" already means the salience
gate's funnel in `docs/salience.md`, and reusing the word for an orthogonal split
would put two meanings of the same term in two prompts and a schema.

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
| Petition granted | `Outcome.actual_granted` |
| Vote split | `Outcome.votes`, tallied |
| Each justice's vote | `Outcome.votes`, per justice |
| Majority author | *no field yet* |
| A concurrence is filed | *no field yet* |
| A dissent is filed | *no field yet* |

### Semantic claims

Require matching a predicted proposition against the actual opinion text, so they
are graded by the cross-evaluator rather than computed.

| Claim | Graded against |
| --- | --- |
| The doctrinal ground of the majority | The majority opinion |
| What a concurrence splits off | The concurrence |
| The argument a dissent rests on | The dissent |

Semantic grades are formed **before** the grader sees which predictor produced
the claim, for the same reason the big-case read is: a grader who knows whose
claim it is will anchor, and the agreement number then measures the anchor.

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
- **The ratio is undefined exactly where claims are most common.** It divides by
  the baseline's Brier, which is zero whenever the baseline predicted the outcome
  perfectly — and the existing implementation returns `None` there. On claims with
  extreme baselines ("a dissent is filed" against a term where one always is) that
  is most of the set.

The two are not in conflict: the ratio answers "how much better than the
baseline, proportionally", for one headline number. The difference answers "how
many Brier units did this claim earn", which is what a sum needs.

### Why a sum, not a mean

A mean rewards abstention. Drop the hardest claim and the mean rises, with no
loss anywhere — precisely the wrong incentive when the point is to elicit more
bits. Under a sum, declining a hard claim moves the total by zero and the
predictor simply earns less.

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

That is a starting posture, not a permanent one. Folding claim scores into a
headline would be a process change, so it moves the process digest and belongs to
its own decision.

## What is scoreable today

Of the ten claims above, **one** can be scored now.

| Claim | Blocked on |
| --- | --- |
| Disposition, petition granted | — *scoreable now* |
| Vote split, each justice's vote | `Outcome.votes` is `[]` in every committed outcome; nothing populates it |
| Majority author, concurrence, dissent | No field on `Outcome`, and no ingestion channel supplies one |
| All semantic claims | `opinion_text` is empty on every corpus row; the evaluator has nothing to read |

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
