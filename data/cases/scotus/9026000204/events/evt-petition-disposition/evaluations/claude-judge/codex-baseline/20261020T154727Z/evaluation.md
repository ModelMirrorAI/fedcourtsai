# Evaluation: codex-baseline

**Cell.** Cert stage (`event.yaml` `stage: cert`), forward. The outcome is `granted` (plenary route, resolved 2026-10-19 after two distributions), and `actual_granted` = 1. The scored prediction froze `context.band: federal` under `sal-v4`, so the segment base rate, the Brier skill score and the basis are the harness's risk-set stamp. I left all three null and compute no rate of my own; comparisons below refer to "the stamped segment base rate". Votes are not scored at the cert stage. This is not a merits cell, so there is no `semantic_grades` block. The harness computes `claim_scores`.

**Result.** Predicted `granted` at P = 0.96, which is correct. Brier = (0.96 − 1)² = 0.0016.

**Reasoning quality: 0.85.** This is the most careful rationale. It states the anchor exactly (143/202 = 0.708 over the nine sal-v4 federal Terms before 2026) and avoids double-counting federal-petitioner status. Its adjustments are grounded in pinpoint citations to the provisioned petition and response. It correctly reads the "brief in opposition" as substantively supporting certiorari despite its label, and it weighs vehicle quality (undisputed standing here) against the companion. It is also disciplined about which statpack cuts it does not transplant (terminal relist buckets used as forward hazards). That separation is sound. Its 0.72 further-distribution call matches the realized relist. Small deductions: it relies only on the advocacy's account of the companion's posture, with no check of it, and the residual 4% is described rather than decomposed.

**Leakage.** Not applicable (forward). Its only external calls were two generic Rules-of-the-Court lookups that returned nothing usable; see `leakage.notes`.
