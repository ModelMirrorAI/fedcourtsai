# Evaluation: claude-baseline

## Outcome and quantitative scores

This is a cert-stage petition-disposition cell, not a merits judgment. The supplied outcome records `actual_disposition=gvr`, `actual_granted=1`, resolved October 13, 2026. The provisioned October 13 snapshot independently records a grant, vacatur, and remand for further consideration in light of Keathley. The scored prediction is the blinded run `20261003T200236Z`, created October 3, 2026.

The prediction names `gvr`, exactly matching the outcome: **correct = 1**. Its grant-family probability is **0.75**, so **Brier = (0.75 - 1)^2 = 0.0625**. A GVR counts as a grant on the binary axis but remains distinct from `granted` on the disposition-label axis.

All baseline and skill fields are left to the harness because this prediction froze an elevated band under sal-v4. Any comparison must use the stamped segment base rate; no independently pooled rate is supplied here. Cert votes are not scored. No judgment accuracy or semantic grades apply, and no claim_scores block is written.

## Reasoning quality: 0.91

The rationale engages directly with the appended appellate opinion and the opposition rather than relying on the successful outcome label. It identifies the superseded inadvertence test, distinguishes a limited remand from a petitioner victory on the underlying dispute, and explains why the opposition's record-specific defense may be left for reconsideration. It recognizes that the broader bad-faith rule was not adopted and gives concrete denial considerations: quantified claims before bankruptcy, the zero valuation, the missing bond claim, and the timing of amendment. These are supported by the staged petition and opposition. Its treatment of a requested response and redistribution also avoids simply equating two distributions with two completed conferences.

Remaining limitations are modest but substantive. The prose sometimes describes the elevated anchor as a once-relisted population despite acknowledging that this docket's second distribution can be a response-related rescheduling. Its statement that the petition has never been considered at a conference is stronger than the distribution entries alone establish. The probability interval is judgmental rather than empirically fitted, and the retrieved general GVR priors are not close judicial-estoppel comparators; the rationale candidly identifies that last limitation. The October 13 outcome is consistent with the proposed mechanism, but does not by itself validate the precise probability.

The quality grade concerns reasoning.md only. The pointer-named predicted_reasoning.md was read for context, not graded; auxiliary structured claims and their outcome matches are reserved for harness scoring. The current reply and resolved snapshot are not treated as proof of what the predictor had available.

## Leakage assessment

The harness log records forward mode, October 3, 2026 calls, and capture coverage 1.0. The lead-case search and cluster lookup carry June 11, 2026 dates. Other visible external queries seek judicial-estoppel GVR analogues and general corpus GVR priors; the prose and retrieval note describe the lead opinion rather than this petition's outcome. No captured document date is on or after this petition's October 13 resolution. The record supplies no sign that an already-decided target case was provisioned forward. The log captures results as metadata/digests, not full result bodies in this staged view, so this is an evidence-based absence of a leakage signal, not a claim of exhaustive visibility. Assessment: retrieved_outcome_material=false, influenced_prediction=not_applicable.

No leakage exclusion is indicated: leakage_suspected is false. The lead authority is a different case and predates this petition's resolution; its use in a forward cell is legitimate. Candidate identity was neither sought nor inferred. This assessment uses the supplied documents and transcript only, with no new case retrieval.
