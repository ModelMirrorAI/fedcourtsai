# Evaluation: codex-baseline

## Outcome and mechanical scores

This is a cert-stage evaluation of prediction run `20261004T180949Z`. The supplied outcome records denial on October 13, 2026, with `actual_granted = 0`. The candidate's `denied` label is an exact match: `correct = 1`. Its grant probability was 0.10, producing `(0.10 - 0)^2 = 0.01`. A single denial cannot establish calibration or refute every alternative the candidate considered.

The prediction froze `baseline`, `sal-v4`, and Term 2026. Baseline, basis, and skill are left to the harness and the stamped segment base rate. No alternative pooled figure is supplied here. Cert votes are not scored. The separate forecast document was read but not graded; quantitative claims are the harness's, and no semantic grades apply.

## Reasoning quality: 0.90

The analysis is balanced, traceable to the supplied briefs, and appropriately separates certworthiness from eventual constitutional merits. It explains the petition's structural-injury and clear-statement theories while identifying the explicit-preclusion distinction, MCorp analogy, retained appellate review, and absence of an inter-circuit split emphasized by the opposition. The provisioned petition and opposition support those descriptions; they are not treated here as independently verified holdings or as the Court's reasons for denial.

The rationale also engages the alternative Johnson hold request rather than treating prompt denial as the only procedural possibility. It explains why the related case might matter and why the government's distinction between constitutional attacks on benefits legislation and structural attacks on agency proceedings weakens the analogy. It discloses the limits of its record and unsuccessful attempts to verify authorities rather than presenting unseen material as confirmed.

Its baseline method identifies the frozen-band reached population, excludes the prediction's own Term, and distinguishes terminal no-relist statistics from the probability faced by a still-open petition. That is the appropriate conceptual conditioning. I have not independently reconstructed its historical statpack calculation; the current committed pack need not have identical counts. The remaining limitation is the largely judgmental size of the upward grant adjustment, including the hold/GVR opportunity. The candidate acknowledges that uncertainty but supplies no matched empirical support for its magnitude. That limits precision without negating the quality of the legal comparison. The score grades this rationale alone, not the separate forecast or realized success of ancillary claims.

## Leakage assessment

The prediction and log are forward and dated October 4, before the October 13 denial. The log captures results for 26 of 29 calls. The three unobserved web calls concern Axon or its 2023 opinion URL; missing result records are not proof that the calls returned nothing, despite the candidate's report of unusable results. Their query subjects are antecedent authority, not this petition's disposition. Nothing in the logged scopes or reasoning shows this petition was already decided. Related-case discussion is permissible forward context. The assessment is `retrieved_outcome_material = false`, influence `not_applicable`, and `leakage_suspected = false`.

## Evidence scope

The assessment uses the supplied outcome, blinded candidate documents and log, the provisioned questions presented and selected petition/opposition passages, the October 13 snapshot, and the committed statpack's population-definition caption. No external case facts or live corpus queries were used. Availability of additional documents in the evaluator's later record is not evidence that the predictor had them.
