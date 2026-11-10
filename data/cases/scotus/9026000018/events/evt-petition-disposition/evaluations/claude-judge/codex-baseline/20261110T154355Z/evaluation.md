# Evaluation: codex-baseline

**Cell.** Cert stage (`stage: cert`, moment `distribution`). Outcome: **denied** on 2026-11-09. `actual_granted` 0, two distributions, no CVSG, no noted dissent or statement. The docket shows the BIO on Oct 2, the reply on Oct 20, redistribution on Oct 21 for the 11/6 conference, and a bare denial on Nov 9. The segment base rate, its basis and the skill score are stamped by the harness from the prediction's frozen `state` band. I quote no rate of my own; comparisons below refer to "the stamped segment base rate". No `claim_scores` and no semantic grades on a cert cell. Vote accuracy is not scored at the cert stage.

**Score.** Predicted `denied` at P(grant) 0.12, so it is correct. Brier = 0.0144.

**Leakage.** Forward mode, run 2026-10-05/06. Its only external retrieval was Turner v. Rogers (2011), through two web searches and CourtListener lookups, and it disclosed this in its reasoning. The two web-search rows are `unobserved`, so I graded them on their queries, which target only Turner. It read nothing under data/qp-topics and made no case-own queries past the snapshot. Graded `not_applicable`, not suspected.

**Reasoning quality: 0.80.** This is the strongest of the three rationales:
- It anchors precisely on the state band, computed from the pack's counts. It explains why terminal relist and CVSG buckets are not forward hazards, which is the error gemini-baseline made.
- It weighs the response request, the en banc split and Turner's duration language, and checked Turner itself.
- It then sets out three distinct obstacles: the final-judgment supersession point (treated as contested, not adjudicated), recurrence and a shallow split.
- The landing at 0.12 follows from the stated weighing. It is also careful about the forward-cell boundary and the response-request field being null in the context.

Minor deductions: the downward adjustment is admittedly judgmental, and the document is somewhat long relative to its decisive points.

## Predicted reasoning

**Grade: 0.85.** Central claims:
1. Denial: borne out.
2. Modal path of one additional distribution after briefing, then denial: borne out (distribution_count 2, denied after the 11/6 conference).
3. Denial without a separate writing: borne out.
4. No CVSG: borne out.
5. If granted, a narrowed QP 1 by summary vacatur: unresolved (conditional on a grant that did not happen).

The document commits to a specific procedural path, and that path matched the docket exactly. It sits just below the top anchor only because "deny, no writing" was the modal expectation for this posture, not a call against the grain.
