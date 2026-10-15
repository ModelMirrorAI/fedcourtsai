# Evaluation — gemini-baseline

**Cell.** Cert stage, forward mode. Outcome: `gvr` (resolved 2026-10-13, two distributions, no CVSG); `actual_granted` = 1. The prediction froze `context.band` = `elevated` under sal-v4, so the segment base rate, skill score, and basis are left to the harness stamp; the comparison anchor is the stamped segment base rate. Votes are not scored on a cert cell. No semantic set is declared on a cert cell, so there is no `semantic_grades` block.

**Score.** Predicted `gvr` at P(grant) = 0.95 → correct = 1, Brier = 0.0025.

**Reasoning quality: 0.62.** The rationale identifies the decisive facts correctly: a GVR request in light of *Durnell*, a response the Court requested after the waiver, the respondent's explicit non-opposition, and distribution for the October 9 conference. Its conclusion is sound. But it is very thin. It says it "adjusted the base rate significantly upward" without naming the base rate or the band. It weighs no residual path to denial (for example a non-label warning theory, or settlement). And it states *Durnell*'s holding with a Westlaw cite without saying where that came from. That cite probably came from the petition, but the rationale does not say so. The stakes reasoning (a routine application of settled precedent) is apt.

**Leakage.** None. The prediction is dated 2026-09-27, before the resolution. Every logged call is unobserved, which is this engine's standing shape. I graded the calls on their queries: all are local reads of the provisioned record, the statpack, and schemas. There are no web or MCP calls.
