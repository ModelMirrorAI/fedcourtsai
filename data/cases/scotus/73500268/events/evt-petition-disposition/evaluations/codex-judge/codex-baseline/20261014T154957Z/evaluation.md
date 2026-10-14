# Evaluation: codex-baseline

## Outcome and quantitative scores

This is a cert-stage petition-disposition cell, not a merits judgment. The supplied outcome records `actual_disposition=gvr`, `actual_granted=1`, resolved October 13, 2026. The provisioned October 13 snapshot independently records a grant, vacatur, and remand for further consideration in light of Keathley. The scored prediction is the blinded run `20261003T200236Z`, created October 3, 2026.

The prediction names `gvr`, exactly matching the outcome: **correct = 1**. Its grant-family probability is **0.82**, so **Brier = (0.82 - 1)^2 = 0.0324**. A GVR counts as a grant on the binary axis but remains distinct from `granted` on the disposition-label axis.

All baseline and skill fields are left to the harness because this prediction froze an elevated band under sal-v4. Any comparison must use the stamped segment base rate; no independently pooled rate is supplied here. Cert votes are not scored. No judgment accuracy or semantic grades apply, and no claim_scores block is written.

## Reasoning quality: 0.94

The rationale clearly separates what the frozen snapshot established, what the separate lead authority supplied, and what remained uncertain. It identifies the restrictive inadvertence formulation in the lower-court appendices, connects it to the intervening standard described in the opposition, and distinguishes that standard from the petition's broader bad-faith theory. It addresses the opposition's strongest factual distinctions in detail, explaining why facts supporting inconsistency or judicial acceptance do not necessarily cure a separately restricted inadvertence inquiry. The resulting remand thesis is supported by the staged documents and consistent with the October 13 disposition, without treating remand as ultimate victory.

The analysis also avoids treating redistribution as proof of repeated substantive conference consideration, distinguishes terminal descriptive cuts from forward hazards, and acknowledges that the reply was not in its prediction-time information set. The precise probability remains an expert judgment rather than a fitted estimate from comparable hold-and-GVR petitions. That residual calibration uncertainty limits an otherwise strong and transparent analysis; the favorable outcome does not eliminate it. No bonus is assigned for the separate forecast document or structured claims.

The quality grade concerns reasoning.md only. The pointer-named predicted_reasoning.md was read for context, not graded; auxiliary structured claims and their outcome matches are reserved for harness scoring. The current reply and resolved snapshot are not treated as proof of what the predictor had available.

## Leakage assessment

The harness log records forward mode and October 3, 2026 calls, with capture coverage 0.9375. The two web calls are unobserved: their null dates cannot corroborate the prose's claim of no usable results. Their visible queries nevertheless concern only Keathley and its opinion URL. Captured calls also seek and read the separate lead opinion; the prose discloses lead-case July remand metadata without treating it as this petition's result. The local find command explicitly excludes data/qp-topics/* and does not read labeling artifacts. Calls classified other remain assessable from their query payloads and are not suspicious merely because the class collapsed. No visible query, result metadata, or reasoning reveals this petition's October 13 disposition before prediction. Assessment: retrieved_outcome_material=false, influenced_prediction=not_applicable.

No leakage exclusion is indicated: leakage_suspected is false. The lead authority is a different case and predates this petition's resolution; its use in a forward cell is legitimate. Candidate identity was neither sought nor inferred. This assessment uses the supplied documents and transcript only, with no new case retrieval.
