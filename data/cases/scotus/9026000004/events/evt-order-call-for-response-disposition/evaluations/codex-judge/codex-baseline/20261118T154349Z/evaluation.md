# Evaluation: codex-baseline

This cert-stage prediction correctly called denial. The outcome records a standard denial on November 16, 2026, `actual_granted: 0`, and no noted dissent. With grant probability 0.14, `correct = 1` and `brier_score = (0.14 - 0)^2 = 0.0196`. Cert votes are not scored. The harness supplies the segment baseline, skill, and mechanical claim scores; no semantic set is declared on this stage.

## Analytical reasoning

`reasoning_quality = 0.92`. The rationale accurately distinguishes the constitutional notice question from the collateral default-judgment dispute. It uses the actual appellate appendix, rather than accepting the petition's wrong-defendant characterization as an adjudicated jurisdictional fact. Its description of the Georgia purchase and injury, venue, default, and limits on reopening the judgment matches App. 2a-13a. It correctly distinguishes forfeiture of an improper-party defense from forfeiture of a personal-jurisdiction objection and acknowledges the absent underlying briefs instead of declaring a preservation failure proved.

The doctrinal discussion also tests the petition's statutory-notice theory against *Mallory* and *Pennsylvania Fire*, recognizing that statutory silence does not itself demonstrate a controlling federal conflict. The staged opposition later advances related objections (BIO pp. 14-28), which supports the plausibility of this analysis without establishing why the Court denied review. The response request and amicus justify some upward adjustment, and the rationale clearly labels the size of that adjustment judgmental. Its precise probability is not empirically derived, but it does not pretend otherwise. A single denial cannot validate that calibration.

I checked statistical use against historical `sal-v4` statpack build `7bcde3b105cb212283905eda17b827efc188e80c`, recovered with `statpack-at`, rather than the currently committed `sal-v8` pack. The stated strictly-prior risk-set counts reproduce that build, and the quoted relist, CVSG, and amicus comparisons include the grant family. The rationale appropriately treats those overlapping terminal populations as descriptive, not independent likelihood ratios or a measured response-request effect. The stamped segment base rate is the scoring anchor; this write-up supplies no substitute.

## Predicted reasoning

`predicted_reasoning_quality = 0.90`. The central claims were denial without a separate writing, one additional distribution after the response, and no CVSG. The staged docket and outcome bear these out: opposition October 14, second distribution October 28 for November 13, plain denial November 16, two total distributions, no CVSG, and no noted dissent or recorded separate writing.

This is more specific than a generic denial forecast because it identifies the modal distribution path and distinguishes routine redistribution from a substantive relist. It gives no precise conference date and describes some outcomes probabilistically, keeping it below the top anchor. Its grant-route and notice-question forecasts were expressly conditional on review; the denial leaves them unresolved, with neither credit nor penalty. The document correctly avoids treating denial as an answer to the due-process question.

## Leakage and significance

This was a forward prediction on October 29, before the November 16 disposition. The harness log shows provisioned-record and statistical reads plus general-precedent retrieval. Its five unobserved web calls all target the 2023 *Mallory* opinion; their missing results are not treated as empty returns. No call or prose indicates access to this petition's later outcome. The petition's later fetch date does not change its preexisting filing date. `influenced_prediction` is `not_applicable` and `leakage_suspected` is false.

My independent significance assessment is 0.50. The notice required for corporate registration to establish general jurisdiction matters beyond this litigation, but a procedurally complicated individual default judgment limits this case's suitability for a broad ruling. The denial resolves no constitutional merits question.
