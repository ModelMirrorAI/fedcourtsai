# codex-baseline — P(grant) 0.32, predicted `denied`

**Cell:** scotus/73281681, `evt-petition-disposition`, stage `cert`. Outcome: `denied` (`actual_granted` 0), resolved 2026-10-13 after three distributions, no CVSG, no noted dissent from denial.

**Base rate.** The prediction froze band `elevated` under `sal-v4`, so the segment base rate, `base_rate_basis`, and Brier skill score are the harness's risk-set stamp. I left them null and quote no rate of my own; comparisons below refer to "the stamped segment base rate". (My own cell's `record/context.json` shows the terminal band `high` with three distributions. That is the decided docket, not the prediction's frozen input, so it is not the anchor.)

**Leakage.** Forward cell: predicted 2026-09-18, about three weeks before the October 13 order. Vote accuracy is not scored at cert. No semantic set is declared at cert, so there is no `semantic_grades` block. `claim_scores` is the harness's.

**Scores.** correct = 1; Brier = 0.32² = 0.1024.

**Leakage: not_applicable.** Retrieval was confined to older precedent: Anderson Creek (N.C. 2022) and Sheetz (2024), via CourtListener. Five web requests were `unobserved`. I graded them on their queries, which all target that same precedent. No query sought this docket or its outcome.

**Reasoning quality: 0.80.** The analysis is careful and well sourced. The anchor pooling is shown term by term (about 17.24%). The candidate checked the claimed split against the North Carolina opinion's own text rather than taking the petition's word. It reads the Sheetz concurrence correctly as signalling an open threshold question. It treats the BIO's vehicle objection (no property interest; voluntary conversion; an independent ground) as substantial but contested. It also explicitly declines to multiply band-encoded signals. Two things pull the score down. First, it did not read the reply, though it says so. Second, it moved further above the anchor than claude-baseline on roughly the same evidence, so it ends somewhat less well calibrated given a denial. The direction and the modal call were right.
