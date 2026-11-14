# Evaluation of `codex-baseline` — `scotus/73280982` (`evt-brief-sg-disposition`)

## Outcome & Score Summary

On November 13, 2026, the Supreme Court granted certiorari limited to the Solicitor General's reformulated Question 1 for plenary review after two post-CVSG distributions (`distribution_count: 3`), with no separate writings (`actual_disposition: "granted"`, `actual_granted: 1`, `disposition_route: "plenary"`).

- **Categorical call (`correct = 0`):** Substantively, `codex-baseline` called the exact real-world action (granting review limited to Question 1 as reformulated by the Solicitor General while declining Question 2), but mapped that action onto `predicted_disposition: "granted-in-part"` rather than `"granted"`. Because SCOTUS orders limiting review to one question read `"Petition GRANTED limited to the following question: ..."` without `"in part"` phrasing, the outcome resolved to `actual_disposition: "granted"`, yielding `correct = 0` under exact-label matching.
- **Probabilistic call (`brier_score = 0.0256`):** `probability = 0.84` against `actual_granted = 1` — a confident, well-calibrated grant probability that substantially beat the stamped segment base rate.
- **Leakage (`leakage_suspected = false`):** Genuine forward forecast placed on October 26, 2026, eighteen days before the November 13, 2026 grant. All 18 logged calls were captured: local reads of the provisioned October 7, 2026 files and `metrics/statpack.md` (deliberately refraining from opening `supplemental-brief.txt` to stay strictly inside the `2026-10-08` snapshot boundary) plus two disclosed CourtListener MCP calls checking *Macquarie Infrastructure Corp. v. Moab Partners, L.P.*, 601 U.S. 257 (`retrieved_doc_date: "2024-04-12"`), with zero `data/qp-topics/` reads or queries on this case.

## Reasoning Quality (`reasoning_quality = 0.86`)

Base-rate citations were checked against the statpack build in force when `codex-baseline` ran (`eb6830084a18`, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`), rather than the later committed `sal-v8` statpack.

**What drove the score upward:**
1. **Strict boundary and prior-Term pooling discipline:** `codex-baseline` caught that `questions-presented.txt` (at prediction time) held a body slice from printed pages 31–33 and verified the actual Questions Presented from `petition.txt` and `sg-invited-brief.txt`, declined to open post-cutoff supplemental briefing, and pooled the `sal-v4` `high` risk-set rows strictly across prior Terms 2017–2024 (`n = 898` weighted, properly excluding the case's own Term 2025). Its CVSG citations (`n = 164` resolved: 29.3% `granted`, 5.5% `gvr`, 62.2% `denied`, 3.0% `dismissed`) matched `eb6830084a18` exactly.
2. **Targeted doctrinal verification and balanced vehicle analysis:** Using CourtListener MCP narrowly to verify *Macquarie*'s exact treatment of pure omissions under Rule 10b-5(b) versus Section 11(a)'s express required-statements text added genuine analytical value. `codex-baseline` weighed the SEC-cosigned SG grant recommendation, recurring mid-quarter IPO exposure, and *Stadnick* tension against respondents' non-adversity framing and the interlocutory Rule 12(b)(6) posture to justify `probability = 0.84` and coherent `cert-v2` secondary claim probabilities (`relist-increment: 0.99`, `cvsg-increment: 0.0`, `summary-disposition-route: 0.02`, `dissent-from-denial: 0.05`).

**Deductions:**
1. **Mis-mapped a limited-question SCOTUS cert grant to `granted-in-part`:** `codex-baseline` selected `predicted_disposition: "granted-in-part"` solely because review would be limited to one of two questions presented, overlooking that SCOTUS limited-question cert grants use `"Petition GRANTED limited to..."` phrasing and resolve to `"granted"` in the pipeline's taxonomy (as visible in `eb6830084a18`'s CVSG breakdown, which carried 29.3% `granted`, 5.5% `gvr`, and no `granted-in-part` bucket despite limited-question CVSG grants being standard practice).

## Predicted Reasoning (`predicted_reasoning_quality = 0.95`)

Graded on `predicted_reasoning.md` alone (independently of `prediction.json`'s categorical enum choice), `codex-baseline`'s forecast document was crisp, specific, and completely borne out by the staged record:

- **Limited grant on SG-reformulated Question 1 and plenary route (`borne-out`):** Committed directly that the Court would grant certiorari limited to Question 1 reformulated along the lines proposed by the Solicitor General, decline the broader Item 303 question, and set the case for plenary briefing and argument rather than GVR or summary reversal.
- **Exact reformulated question substance (`borne-out`):** Accurately stated the substance of the adopted question — whether an issuer may be held liable under Section 11(a)'s misleading-omissions clause based on a materiality finding for undisclosed interim financial information without a separate determination that an affirmative statement was rendered misleading — matching the November 13, 2026 order.
- **November 2026 conference timing and relist path (`borne-out`):** Specifically forecast redistribution for a November 2026 conference following Rule 15.8 supplemental briefs and action either on the first post-SG distribution or after a single relist for wording checks; the petition was distributed for November 6, relisted once on November 9 (`distribution_count: 3`), and granted on November 13, 2026.
- **Unsigned order with no separate writing (`borne-out`):** Correctly committed to an unsigned order-list entry with no separate statement as the modal outcome.
