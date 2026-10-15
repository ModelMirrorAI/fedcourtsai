# gemini-baseline — P(grant) 0.52, predicted `granted`

**Cell:** scotus/73281681, `evt-petition-disposition`, stage `cert`. Outcome: `denied` (`actual_granted` 0), resolved 2026-10-13 after three distributions, no CVSG, no noted dissent from denial.

**Base rate.** The prediction froze band `elevated` under `sal-v4`, so the segment base rate, `base_rate_basis`, and Brier skill score are the harness's risk-set stamp. I left them null and quote no rate of my own; comparisons below refer to "the stamped segment base rate". (My own cell's `record/context.json` shows the terminal band `high` with three distributions. That is the decided docket, not the prediction's frozen input, so it is not the anchor.)

**Leakage.** Forward cell: predicted 2026-09-18, about three weeks before the October 13 order. Vote accuracy is not scored at cert. No semantic set is declared at cert, so there is no `semantic_grades` block. `claim_scores` is the harness's.

**Scores.** correct = 0; Brier = 0.52² = 0.2704.

**Leakage: not_applicable.** The log has `result_capture_coverage` 0.0 (every call `unobserved`), so I graded it on its queries. These were one CourtListener precedent search ("Nollan" AND "Dolan" AND "Koontz") and a corpus query that failed on invalid arguments. None targets this case's outcome. The reasoning shows no post-snapshot facts.

**Reasoning quality: 0.35.** The candidate identified the right raw ingredients: the band anchor, the response requested after a waiver, the five amici, and the BIO's vehicle objections. But it more than tripled the anchor, to 0.52, on an unsupported assertion that this combination "typically pushes the grant probability into the 40-60% range". No statpack figure or cited rate backs that up. It counted counsel identity and amicus volume as strong grant signals without discounting for how often such petitions are denied. It also brushed off the BIO's independent state-law holding as "standard fare", which is the opposite of the weight it deserved. The log shows the candidate read only the head of the BIO and grepped it, and never opened the petition. The reasoning also misstates its own anchor window ("ten Terms prior"), whereas the rendered table shows OT2017 to OT2024. The prose is thin relative to the size of the departure from base rate, and the call was wrong.
