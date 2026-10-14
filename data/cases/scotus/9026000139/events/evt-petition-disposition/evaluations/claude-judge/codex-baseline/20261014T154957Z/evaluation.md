# Evaluation — codex-baseline

**Cell.** Cert stage, forward mode. Outcome: `gvr` (resolved 2026-10-13, two distributions, no CVSG); `actual_granted` = 1. The prediction froze `context.band` = `elevated` under sal-v4, so the segment base rate, skill score, and basis are left to the harness stamp; the comparison anchor is the stamped segment base rate. Votes are not scored on a cert cell. No semantic set is declared on a cert cell, so there is no `semantic_grades` block.

**Score.** Predicted `gvr` at P(grant) = 0.97 → correct = 1, Brier = 0.0009.

**Reasoning quality: 0.88.** This is a careful, well-anchored rationale. It pools the elevated-band reached rate from the statpack (about 16.9%) and then moves far up from it on evidence it names: the QP asks only for a remand in light of *Monsanto v. Durnell* (June 25, 2026); the jury rejected design defect, so only failure-to-warn theories survived; and, most decisive, the court-requested response expressly does not oppose a GVR. It treats the second distribution correctly as a redistribution after the response request, not a post-conference relist. It also separates a GVR from plenary review and is candid about what it did not verify. It is weaker than it could be on one point: it did not check the post-*Durnell* GVR analogs in the corpus. It relied on the petition's advocacy for those, but it labels them as such. The 3% residual is reasonable.

**Leakage.** None. The prediction is dated 2026-09-27, before the resolution. Its only external calls were two web searches on general GVR doctrine. A `find` in its log excludes `data/qp-topics/` with `-not -path`, so it opened nothing there and that is not a read.
