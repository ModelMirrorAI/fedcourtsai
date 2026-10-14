# Evaluation — gemini-baseline

**Cell.** scotus/9026000006 (Merritt v. Texas Farm Bureau), `evt-petition-disposition`, stage `cert`. Outcome: `denied` on 2026-10-13, after a single distribution for the October 9, 2026 conference, with no noted dissent (`actual_granted` 0).

**Base rate.** The scored prediction froze a band (`baseline`, `sal-v4`), so the segment base rate, its basis and the Brier skill score are the harness's risk-set anchor, filled in by `stamp-cell`. I leave them null here and quote no rate of my own. Compare against the stamped segment base rate.

**Leakage.** Forward cell: the prediction is dated 2026-10-04, before the conference and the denial. I checked the log for this case's own disposition showing up as already decided and found none (details below).

**Score.** Predicted `denied`, P(grant) = 0.015. Correct (1). Brier = 0.015² = 0.000225.

**Reasoning quality: 0.60.** The core moves are right. The candidate anchors on the baseline band's reached rate (~4–6%) and adjusts down because there is no circuit split and the petition asks for error correction. It also uses the BIO's argument that no conflict exists. But the rationale is a single paragraph, and it has two weaknesses. First, it calls the dispute "fact-bound" and "application ... to a jury's factual findings." The QP is in fact a clean statutory question: does "suffer or permit" dispense with employer knowledge? So the candidate missed the strongest pro-grant point and never weighed it. Second, it never mentions the vehicle problems that make a denial overdetermined: the preservation dispute and the unchallenged deliberate-prevention instruction. It does not show its pooling of the anchor either. The number is well calibrated. The analysis supports it only thinly.

**Leakage.** Every log call reads a provisioned input or the committed statpack. There are no web, MCP or corpus lookups. All calls are `unobserved` (coverage 0.0), so I graded them on their queries, and none seeks this case's outcome. Grade: `not_applicable`, not suspected.
