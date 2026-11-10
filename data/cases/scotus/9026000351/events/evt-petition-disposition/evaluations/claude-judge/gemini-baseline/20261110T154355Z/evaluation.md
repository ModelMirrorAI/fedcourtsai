# Evaluation — gemini-baseline

**Cell.** Cert stage, forward mode, *Dreiling v. United States*, No. 26-351. The snapshot shows the petition filed Aug 14 2026, the United States waiving its response Oct 16, one distribution Oct 21 for the Nov 6 conference, and "Petition DENIED." on Nov 9 2026. The outcome is `denied`, `actual_granted` 0, distribution_count 1, no CVSG, no noted dissent. The segment base rate and skill score are left for the harness to stamp (frozen `baseline` band, sal-v4, risk-set basis). I quote no rate of my own; see the stamped segment base rate.

**Score.** The candidate predicted `denied` at P(grant) = 0.002, so `correct` = 1 and Brier = 0.000004.

**Reasoning quality: 0.85.** The analysis was strong and well evidenced. It went through all three QPs: QP 1 was not reached below (it cites the petition's own footnote acknowledging this), the panel addressed QP 2, and QP 3 asks to overturn settled money-mandating precedent with no split possible. It gave weight to the pro se posture and the waiver. It used the corpus legitimately, confirming that the petitioner's two related filings (Nos. 25-1217 and 26-9) were each denied after one distribution, before this prediction was made. Its base-rate use matched the sal-v4 baseline risk set. Two deductions: it asserts a lack of standing or cause of action that neither court below decided, and it says the Federal Circuit "correctly held", which is advocacy where analysis was called for. Neither affects the soundness of the forecast.

**Predicted reasoning: 0.7.** I treated five claims as central: denial at the first conference (Nov 6), no relist, no response request or CVSG, no dissent or statement, and the conditional threshold-QP route. The first four were specific and were all borne out. The conditional content was never tested. As with any near-default denial, the claims carry limited discriminating content, so the grade sits below the top.

**Leakage.** The cell is forward. The prediction was made 2026-10-23, before the 2026-11-09 resolution. I found no retrieval of this petition's disposition and no read inside `data/qp-topics/`. Graded `not_applicable` / `retrieved_outcome_material: false`. Corpus queries reached only the petitioner's earlier dockets, both resolved before the prediction.

**Big case.** My own read is 0.15. The judicial-discipline backdrop is real, but this vehicle is a pro se collateral Tucker Act suit, disposed of below on jurisdiction in a nonprecedential order and denied without comment.
