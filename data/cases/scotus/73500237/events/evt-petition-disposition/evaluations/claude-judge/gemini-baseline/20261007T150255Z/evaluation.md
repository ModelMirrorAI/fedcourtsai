# Evaluation of gemini-baseline — Redding v. Mullin, No. 25-1336 (evt-petition-disposition)

**Stage: cert.** Outcome: petition **denied** on 2026-10-05 after one distribution
(long conference of 9/28/2026), no CVSG, no noted dissent. The candidate
predicted `denied` at P(grant) = 0.015, so `correct` = 1 and Brier = 0.000225.

## Base rate and skill

The prediction froze `band: baseline` with `salience_version: sal-v4`, matching
the statpack's sal-v4 band table heading, so the basis is `risk_set`. Pooling
the bracketed `reached` figure for `baseline`, resolved-weighted, over OT2017
through OT2024 (every rendered Term strictly before Term 2025; the caption shows
10 of 10 Terms, so no lookback divergence) gives 0.0512 on n = 11,580. Brier
skill score = 1 − 0.000225 / 0.0512² ≈ 0.914. The candidate quoted the same
≈5.1% anchor.

## Reasoning quality: 0.50

The rationale reaches the right number by the right headline signal, but it is
thin and carries two analytic errors that the provisioned record alone would
have corrected:

- It treats the statpack's relist-0 bucket (≈1.2% granted) as "a significantly
  lower historical grant rate" for a petition at its first distribution. That
  cut is a terminal description of petitions that ended with zero relists, not
  the hazard a petition still at its first conference faces; a petition that
  will be relisted and granted is in a different bucket. The prompt's warning
  that the pooled cuts are shape, not forward rates, applies here.
- It says the asserted conflict with A.J.T. v. Osseo "could theoretically
  invite a GVR". A.J.T. was decided in June 2025 and the Fourth Circuit ruled
  in March 2026, dates the petition itself gives, so A.J.T. is not an
  intervening decision and a GVR in light of it is not a live route. The
  other two candidates caught this.

It does not engage the Fourth Circuit opinion in the appendix at all, so it
misses the two independent grounds (pleaded inability to perform the desired
position's essential functions; a reasonable reassignment actually provided)
that are the strongest vehicle argument against review. The SG waiver point
and the CVSG point are right. One further note: its retrieval.md reports no
retrieval beyond the provisioned inputs, but the captured log carries a corpus
query on 2020s SG-waiver priors (result unobserved). That is a disclosure
inaccuracy rather than a leakage concern, and it does not enter this score. I
do not score the claims block or the forecast document.

## Leakage

Mode `forward`; prediction created 2026-09-17, resolution 2026-10-05. The log
(26 calls, capture coverage 0.0, which is this engine's standing shape) shows
reads of the provisioned inputs and the statpack, plus the one corpus query
above, graded on its query since no result reached the log. Nothing targets
this case's disposition. `retrieved_outcome_material` = false,
`influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My own read is 0.10: an individual federal-employment accommodation dispute
dismissed on the pleadings, no joined split, SG waiver, one-pass denial
without writing. The predictor's score was visible in its prediction.json
before I wrote mine, so my read rests on the record and outcome rather than
being formed in isolation; I note that for the panel.
