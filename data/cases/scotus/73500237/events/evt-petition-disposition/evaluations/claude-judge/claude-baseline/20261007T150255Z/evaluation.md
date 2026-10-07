# Evaluation of claude-baseline — Redding v. Mullin, No. 25-1336 (evt-petition-disposition)

**Stage: cert.** Outcome: petition **denied** on 2026-10-05 after one distribution
(long conference of 9/28/2026), no CVSG, no noted dissent. The candidate
predicted `denied` at P(grant) = 0.012, so `correct` = 1 and Brier = 0.000144.

## Base rate and skill

The prediction froze `band: baseline` with `salience_version: sal-v4`, and the
statpack's "Segment base rate by salience band (sal-v4)" heading matches, so the
basis is `risk_set`. I pooled the bracketed `reached` figure for `baseline`,
resolved-weighted, over the Term rows strictly before Term 2025 (OT2017 through
OT2024, all eight rendered; the caption says 10 of 10 Terms are shown, so the
rendered window is the pack's full window and no lookback divergence arises):
0.0512 on n = 11,580. Brier skill score = 1 − 0.000144 / 0.0512² ≈ 0.945. The
candidate itself quoted the same pooled anchor (≈5.1%).

## Reasoning quality: 0.85

The rationale is the strongest of the three. Its anchor is the right table,
the right column, and the right leakage-safe window. Its downward moves are
specific and each one checks out against the provisioned petition text:

- The SG waiver (June 17, 2026 entry) and the absence of any call for a
  response over three months are read correctly as the dominant signal.
- The two independent grounds of the Fourth Circuit opinion (not a qualified
  individual by her own pleading; a reasonable reassignment actually provided)
  are accurately drawn from Appendix A, and the point that the first ground
  moots every question presented is the right vehicle analysis.
- It correctly observes that the panel did not join the asserted
  interactive-process split, and that A.J.T. v. Osseo (June 2025) predates the
  March 2026 decision below, so there is nothing for a GVR to be "in light of".
- The drafting lapses it cites (the garbled QP I, the Fourth Amendment in the
  provisions-involved section, the "Noem" appendix caption against the "Mullin"
  docket caption) are all present in the staged petition.

Weaknesses: the counsel-profile heuristic drawn from a corpus pull of granted
priors is thin evidence and is weighted lightly, which is fair; the "where to
discount me" section is candid about not having the district-court opinion.
The number is a defensible quarter of the anchor. I do not score the claims
block or the forecast document.

## Leakage

Mode `forward`; prediction created 2026-09-17, resolution 2026-10-05, so the
case was genuinely open. The log (28 calls, full result capture) shows one
corpus query for granted 2020s priors (document date 2025-02-11) and two
CourtListener docket searches, one on this docket number, both captured with
zero results. Nothing retrieved postdates the event or touches this case's
disposition. `retrieved_outcome_material` = false, `influenced_prediction` =
`not_applicable`, `leakage_suspected` = false.

## Big case

My own read is 0.10: an individual federal-employment accommodation dispute
dismissed on the pleadings, no joined split, SG waiver, one-pass denial
without writing. The predictor's score was visible in its prediction.json
before I wrote mine, so my read rests on the record and outcome rather than
being formed in isolation; I note that for the panel.
