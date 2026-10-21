# Evaluation: gemini-baseline

**Cell.** Cert stage (`event.yaml` `stage: cert`), forward. The outcome is `granted` (plenary route, resolved 2026-10-19 after two distributions), and `actual_granted` = 1. The scored prediction froze `context.band: federal` under `sal-v4`, so the segment base rate, the Brier skill score and the basis are the harness's risk-set stamp. I left all three null and compute no rate of my own; comparisons below refer to "the stamped segment base rate". Votes are not scored at the cert stage. This is not a merits cell, so there is no `semantic_grades` block. The harness computes `claim_scores`.

**Result.** Predicted `granted` at P = 0.95, which is correct. Brier = (0.95 − 1)² = 0.0025.

**Reasoning quality: 0.60.** The core logic is right but thin. It uses the federal-petitioner band as its anchor, adjusts upward because a federal statute was invalidated, and cites the acknowledged CA6 split. It never states a pooled anchor figure, only a range of per-Term values ("52% to 89%"). It misses the strongest case-specific signal: the respondents' brief asks the Court to grant. It also does not engage the vehicle question, meaning the companion *Ream* petition and a possible hold. The statement that the Court "almost always" grants in this posture is asserted, not sourced. The number lands well, but the rationale shows little of the work that would justify 0.95 over, say, 0.85.

**Leakage.** Not applicable (forward). Every call in the log is unobserved, so I graded them on their queries; none targets this petition's disposition. See `leakage.notes`.
