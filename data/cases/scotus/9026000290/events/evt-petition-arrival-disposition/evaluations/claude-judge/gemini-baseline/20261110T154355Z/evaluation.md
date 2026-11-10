# Evaluation — gemini-baseline, evt-petition-arrival-disposition (scotus/9026000290)

**Stage:** cert (arrival moment, forward). **Outcome:** `denied` on 2026-11-09 after one distribution (conference of 11/6/2026). There was no CVSG and no noted dissent.

## Score

- Predicted `denied` with P(grant) = 0.001. `correct` = 1; Brier = 0.001² = 0.000001.
- The segment base rate, its basis and the skill score are left to the harness stamp. Compare against "the stamped segment base rate".
- No votes were predicted, and votes are never scored on a cert cell.

## Reasoning (`reasoning_quality` = 0.65)

The rationale is short but names the right considerations:
- The anchor is the `baseline` band's bracketed reached rate of roughly 5%. That is consistent with the build the candidate ran against, which I rebuilt with `statpack-at` (2420d5dd72e1; it pools to ≈5.02%).
- It identifies the pro se filer, the local fence-and-trellis dispute and the absence of a split.
- It notes that the "plain view as seizure of knowledge" theory runs against *Ciraolo*.
- It notes the pleading-stage dismissals and the denial of state supreme court review.

It is thin on the vehicle. It does not discuss the unexplained writ-denial posture or reviewability. It also does not justify moving from 5% to 0.1%, a factor of about 50, beyond calling the chance "virtually no". The direction and size of the move are defensible for a pro se paid petition, but the analysis behind them is mostly asserted rather than worked through.

## Leakage

The cell is forward. The prediction was made 2026-09-27. The log has 18 calls, all unobserved by engine telemetry. Their queries are reads of the provisioned inputs and the committed statpack, plus writes of the candidate's own outputs. There were no web, MCP or corpus calls and no reads of `data/qp-topics/`. The grade is `not_applicable`.

## Big case

My own read is 0.03.

## Predicted reasoning (`predicted_reasoning_quality` = 0.50)

The central claims were:
- An implied denial ("grant is highly unlikely") — **borne out**.
- No relists — **borne out**.
- No CVSG — **borne out**.
- No separate writing — **borne out**.

All of them held, but the document is generic. It commits to nothing beyond the modal path: no timing and no distribution count beyond "no relists". It never states the disposition outright. The conditional statements about which question would be taken and about a GVR depended on a grant that never happened, so they earn nothing either way. That places it at the "right in direction but generic" anchor.
