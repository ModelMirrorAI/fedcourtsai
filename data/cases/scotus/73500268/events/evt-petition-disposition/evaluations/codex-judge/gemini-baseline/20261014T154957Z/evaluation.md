# Evaluation: gemini-baseline

## Outcome and quantitative scores

This is a cert-stage petition-disposition cell, not a merits judgment. The supplied outcome records `actual_disposition=gvr`, `actual_granted=1`, resolved October 13, 2026. The provisioned October 13 snapshot independently records a grant, vacatur, and remand for further consideration in light of Keathley. The scored prediction is the blinded run `20261003T200236Z`, created October 3, 2026.

The prediction names `gvr`, exactly matching the outcome: **correct = 1**. Its grant-family probability is **0.92**, so **Brier = (0.92 - 1)^2 = 0.0064**. A GVR counts as a grant on the binary axis but remains distinct from `granted` on the disposition-label axis.

All baseline and skill fields are left to the harness because this prediction froze an elevated band under sal-v4. Any comparison must use the stamped segment base rate; no independently pooled rate is supplied here. Cert votes are not scored. No judgment accuracy or semantic grades apply, and no claim_scores block is written.

## Reasoning quality: 0.79

The rationale identifies the central record-supported mechanism: the petition requested a hold and GVR, the appended appellate decision uses the restrictive knowledge/potential-motive test, and the opposition acknowledges the intervening totality inquiry while resisting remand on the facts. This is a coherent reason to depart substantially from a generic petition baseline. The October 13 order follows that proposed route, but the correct result alone does not establish analytical quality or calibration.

The analysis is comparatively thin on the strongest contrary evidence. It mentions the opposition's argument without examining the pre-bankruptcy quantified claims, zero valuation, omitted bond claim, and belated amendment that make that argument substantial. Nor does it explain the distinction between rejecting the restrictive inadvertence test and adopting a categorical bad-faith requirement. The asserted near-certainty is therefore less fully justified than the directional GVR call. The baseline discussion does not document a strictly-prior-Term pooling method. These are limitations of the analysis, not penalties for brevity or for any unscored auxiliary forecast.

The quality grade concerns reasoning.md only. The pointer-named predicted_reasoning.md was read for context, not graded; auxiliary structured claims and their outcome matches are reserved for harness scoring. The current reply and resolved snapshot are not treated as proof of what the predictor had available.

## Leakage assessment

The harness log records forward mode and October 3, 2026 calls, before this petition's October 13 resolution. Its 26 calls all have unobserved results (capture coverage 0.0); null result dates do not establish empty searches. The visible external queries concern the separate lead case, docket 25-6/Keathley, including a dated corpus-query attempt. Local reads concern provisioned inputs and the statpack. The prose describes the October 9 conference as future and does not reveal this petition's disposition. No affirmative evidence shows target-case outcome retrieval or mis-provisioning. Assessment: retrieved_outcome_material=false, influenced_prediction=not_applicable; confidence is limited by absent result capture, not by evidence of contamination.

No leakage exclusion is indicated: leakage_suspected is false. The lead authority is a different case and predates this petition's resolution; its use in a forward cell is legitimate. Candidate identity was neither sought nor inferred. This assessment uses the supplied documents and transcript only, with no new case retrieval.
