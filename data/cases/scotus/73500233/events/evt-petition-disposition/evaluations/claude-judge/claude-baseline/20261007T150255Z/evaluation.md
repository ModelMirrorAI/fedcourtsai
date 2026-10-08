# Evaluation: claude-baseline

**Outcome.** Cert denied on the October 5, 2026 order list after the September 28 long conference, with one distribution, no call for a response, no CVSG, and no noted dissent. The event stage is `cert`.

**Scores.** `predicted_disposition` = `denied` matches, so `correct` = 1. P(grant) = 0.01 against `actual_granted` = 0 gives a Brier of 0.0001.

**Baseline.** Frozen `band` = `baseline` under `salience_version` = `sal-v4`, matching the statpack table's heading, so the basis is `risk_set`: the bracketed `reached` figure for `baseline`, resolved-weighted over the rendered Terms 2017 through 2024 (the caption renders 10 of 10 Terms, so the rendered window is the pack's whole window), about 593 weighted grants over n = 11,580, rate 0.0512. Brier skill = 0.962.

**What the reasoning got right.** The anchor is computed correctly and shown as a table, and the candidate correctly explains why the bracketed figure is the one it is scored against. The adjustments are all mechanism-level rather than impressionistic: the Court does not grant from a response-waived posture without first calling for a response, so a grant needs two unlikely steps; the relist-0 bucket of the paid relist cut is where this petition most likely ends, at roughly a 1.2% grant plus 0.5% GVR; the petition itself concedes no precedent either way; the vehicle problems (no trial objection, ineffective-assistance framing, unpublished per curiam, state supreme court denial without opinion) are read off the petition's own account; and the stacked multi-clause question presented is identified as something the Court would have to rewrite. It also states a floor (0.007) and the one path that could move the number (a call for response at the long conference), which is exactly what did not happen. The retrieval section discloses the 429 and the unused corpus query without being asked.

**What I would mark down.** The counsel-and-presentation point (local firm, citation errors, short brief) is asserted rather than shown, and it is the weakest of the five adjustments. The summary-route conditional at 0.35 is derived from a band GVR share rather than from any intervening decision, which the candidate itself says does not exist; that number is a claim and is scored in code, not here. The rationale is marginally stronger than codex-baseline's on the procedural mechanism that actually governed this petition and marginally weaker on doctrine.

**Reasoning quality: 0.86.**

**Leakage.** Forward cell. The 21-call log is shell and file reads of the provisioned inputs, one corpus query whose single legible document date is September 16, 2026 (before the event, and the candidate says the rows were unrelated and unused), and one CourtListener docket search for No. 25-1333 that was throttled with a 429 and not retried, so no result for this docket reached the agent. No `retrieved_doc_date` at or after October 5, 2026. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The retrieval note matches the log.

**Big case.** My own read, formed before looking at the candidate's score: 0.10. A single state defendant's evidentiary objection, unpublished below, no split, waiver, no amici, denied silently. The candidate's 0.08 is close to mine. No agreement number is computed here.
