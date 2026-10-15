# claude-baseline — P(grant) 0.24, predicted `denied`

**Cell:** scotus/73281681, `evt-petition-disposition`, stage `cert`. Outcome: `denied` (`actual_granted` 0), resolved 2026-10-13 after three distributions, no CVSG, no noted dissent from denial.

**Base rate.** The prediction froze band `elevated` under `sal-v4`, so the segment base rate, `base_rate_basis`, and Brier skill score are the harness's risk-set stamp. I left them null and quote no rate of my own; comparisons below refer to "the stamped segment base rate". (My own cell's `record/context.json` shows the terminal band `high` with three distributions. That is the decided docket, not the prediction's frozen input, so it is not the anchor.)

**Leakage.** Forward cell: predicted 2026-09-18, about three weeks before the October 13 order. Vote accuracy is not scored at cert. No semantic set is declared at cert, so there is no `semantic_grades` block. `claim_scores` is the harness's.

**Scores.** correct = 1; Brier = 0.24² = 0.0576.

**Leakage: not_applicable, nothing retrieved about the outcome.** The candidate fetched this docket's supremecourt.gov feed (no entry after Aug 19, 2026), the cert reply (Aug 17), and the Sheetz II docket (denied June 15, 2026). All of this predates resolution and is legitimate forward signal. The candidate disclosed it openly, which counts in the cell's favour.

**Reasoning quality: 0.85.** This is the strongest analysis of the three. It pools the band anchor correctly (prior Terms only, about 17%). It separates the adjustments the band already encodes from those it does not (a response requested after a waiver; the amicus count). It names the BIO's threshold alternative holding (no property interest in unrestricted residential use) as the largest discount. That vehicle problem is the most plausible reason for the denial. It also flags that the docket's distribution count overstates real relist history. The roughly 1.4× uplift and the reading of the Sheetz II denial as "selecting this vehicle" are judgement calls. The second is a little speculative, and the candidate admits it has no calibrated rate for responses called after a waiver. Overall it is well calibrated: modestly above the anchor, with denial clearly modal.
