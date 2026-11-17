# Evaluation — codex-baseline — Trump v. Thakur, No. 26-210 (cert stage)

**Outcome:** petition denied on 2026-11-16 after a single distribution, no noted dissent.
**Prediction:** `granted`, P(grant) = 0.80. `correct` = 0; Brier = (0.80 − 0)² = 0.64. The segment base rate and skill are the harness's to stamp.

## What it got right and wrong

This is the most careful document on the record and the worst-scoring number. Its handling of the quantitative material is accurate against the statpack build it was placed against (`statpack-at` build dedb32b153e6): the pooled federal anchor, the terminal relist buckets (≈1.8% / 13.5% / 41.2% / 37.1%), the CVSG and amicus cuts, and the correct caution that terminal marginal rates are not forward transition probabilities. Its reading of the filings is also accurate, including the reply's point that district-court proceedings on these claims were stayed by agreement, which genuinely reduces mootness risk, and its check of Finley's reservation for as-applied challenges.

The error is in the judgment step. It identified the absence of a circuit split as the opposition's strongest argument, noted the preliminary-injunction posture and the possible alternative statutory grounds, and then adjusted *upward* from an already high anchor by 6.6 points, on stakes and vehicle stability. The Court denied at the first conference without a noted dissent. An anchor of 0.73 already prices in that SG petitions are usually important; the case-specific evidence it had collected (no split, interlocutory, other circuits pending) pointed down, not up, and it said so itself before going the other way. It labelled the adjustment judgmental, which is honest, but it was the wrong sign.

## reasoning_quality = 0.4

Accurate facts, disciplined base-rate use and candid limits, undone by weighing the cert-stage considerations in the direction the outcome contradicts, at high confidence.

## Predicted reasoning — 0.15

Central claims: a plenary grant — failed; one or two further distributions (0.66) — failed, since the petition was denied off its first conference; no CVSG — held, but never at issue; and, if denied, no noted dissent or statement (0.80) — held on the branch that occurred. The discussion of what the Court would take the case to decide is conditional on a grant and earns nothing either way. The forecast was wrong in direction on both of its leading calls; the denial branch was right but brief and flagged as not the central forecast.

## Leakage

Forward cell, run 2026-11-02. The two web-search rows are `unobserved` and were graded on their queries, which target the 1998 Finley decision only. No own-case disposition material; `not_applicable`.
