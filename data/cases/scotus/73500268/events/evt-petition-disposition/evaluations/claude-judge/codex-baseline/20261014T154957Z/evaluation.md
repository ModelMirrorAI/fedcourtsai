# Evaluation — codex-baseline, scotus/73500268 evt-petition-disposition

**Outcome:** GVR (`actual_disposition` gvr, `actual_granted` 1), resolved 2026-10-13.

**Prediction:** `gvr`, P(grant) 0.82. Correct label; Brier (0.82 − 1)² = 0.0324. This is a cert cell and the prediction froze a band (`elevated`, sal-v4), so the segment base rate, skill and basis come from the harness stamp; `correct` / `brier_score` are stamped over and these values are my independent read.

**Reasoning quality 0.86.** The analysis is careful and well sourced:
- It anchors on the frozen band and shows its pooling.
- It explicitly declines to multiply the terminal-bucket cuts in as if they were independent likelihood ratios, which is correct.
- It ties the upward move to specific pages of the record. Appendix A at 8a–9a and Appendix B at 21a–22a apply the knowledge-or-potential-motive test. The *Keathley* pages it cites require a totality-of-circumstances inquiry and reserve the bad-faith question, which supports a narrow remand rather than plenary review.
- It treats the opposition's argument from the facts of this record fairly, and gives a sound reason why that argument does not cure the legal error: a GVR leaves the record assessment to the Fifth Circuit.
- Like claude-baseline, it correctly reads the second distribution as a reschedule rather than a substantive relist.

Small deductions: 0.82 is still somewhat conservative given its own analysis, and the reply brief was not read (disclosed). The 0.28 stakes score is a judgment call, and I do not grade it here.

**Leakage:** forward cell. CourtListener returned metadata for *Keathley*'s own July 2026 Fifth Circuit remand, a different case that predates this resolution. The candidate disclosed it and did not open it. Two web calls left no captured result, and their queries target only the *Keathley* opinion. One `find` command used `-not -path 'data/qp-topics/*'`, which is an exclusion and not a read. Graded `not_applicable`.

**Semantic grades:** none. This is a cert cell.
