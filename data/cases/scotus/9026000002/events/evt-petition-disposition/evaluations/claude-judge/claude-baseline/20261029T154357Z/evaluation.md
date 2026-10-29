# claude-baseline — scotus/9026000002, evt-petition-disposition

## Outcome and scoring

Cert-stage cell (`stage: cert`), forward mode. Outcome: `dismissed`, `actual_granted` 0, resolved 2026-10-26 — the docket shows a joint stipulation to dismiss under Rule 46 filed 2026-10-23 and "Petition Dismissed - Rule 46" on 2026-10-26. All three candidates predicted `denied`, so `correct` = 0 for each on the exact-label axis (dismissed ≠ denied), though each was right on the binary no-grant axis that the Brier score reads.

The prediction froze `band: baseline` under `sal-v4`, so the segment base rate, skill score and basis are the harness's risk-set stamp; I left them null and refer only to "the stamped segment base rate".

Leakage: forward; prediction made 2026-10-06 against a snapshot ending 2026-08-14, a fortnight before the Rule 46 stipulation existed. No retrieved document dates on or after resolution, no query reaching this docket's disposition, no qp-topics read. `not_applicable`, `leakage_suspected` false.

No semantic set is declared on a cert cell, so no `semantic_grades`. Votes not scored (cert stage).

## This candidate

P(grant) 0.19, predicted `denied`. Brier 0.0361.

**reasoning_quality 0.8.** The strongest analysis of the three. It read the full provisioned record, anchored on the pooled `baseline` bracketed reach rate with figures shown, then built the grant probability structurally: P(lead grant) × P(consolidation or hold-then-GVR), which is the correct model for a petition that asks to be held. Its forward retrieval of the lead docket, its BIO and reply was legitimate (forward cell, open case) and materially improved the analysis — surfacing the Seventh Circuit's *Kim v. Jump Trading* deepening of the split, the lead's vehicle problems (no live foreign party, independent primary holding), and the prospect of a cleaner vehicle. It listed downward factors honestly and named its biggest uncertainty.

Notably, it explicitly priced a dismissal/withdrawal residual, observing that a district-court bench trial had been set for August 10, 2026 "so settlement is live" — the route this petition actually took via Rule 46. It still (reasonably) predicted `denied` as the modal label.

Minor weaknesses: the "one in seven or eight" rate for response-requested petitions is asserted without a cited source, and the lead-grant estimate of 0.28 is judgmental.
