# Evaluation — codex-baseline

**Cell.** Cert stage, forward mode, *Dreiling v. United States*, No. 26-351. The snapshot shows the petition filed Aug 14 2026, the United States waiving its response Oct 16, one distribution Oct 21 for the Nov 6 conference, and "Petition DENIED." on Nov 9 2026. The outcome is `denied`, `actual_granted` 0, distribution_count 1, no CVSG, no noted dissent. The segment base rate and skill score are left for the harness to stamp (frozen `baseline` band, sal-v4, risk-set basis). I quote no rate of my own; see the stamped segment base rate.

**Score.** The candidate predicted `denied` at P(grant) = 0.002, so `correct` = 1 and Brier = 0.000004.

**Reasoning quality: 0.85.** The analysis was sound and carefully bounded. It correctly identified the decisive vehicle problem: the Federal Circuit affirmed a jurisdictional dismissal under *Navajo Nation*, so QP 1 is never reached. It noted that the panel expressly addressed the recusal question, that there is no conflict, and that the United States waived its response. It anchored on the sal-v4 baseline-band risk-set rate pooled over Terms before 2026, and stated plainly that its adjustments were judgment. It was honest about failed retrieval (HTTP 429) and about relying on the provisioned orders. It loses a little for not weighting the petitioner's pro se status or the earlier related denials, which were visible in the petition, and for one loose line on the conditional summary route.

**Predicted reasoning: 0.7.** I treated four claims as central: denial without a separate writing after the Nov 6 conference, no relist, no CVSG or response request, and the conditional QP choice. The first three were specific and were all borne out. The conditional content was never tested. The grade sits below the top because these calls are close to the default for a waived, pro se, paid petition. They are specific in timing and track, but a competent reader would rarely have called them otherwise.

**Leakage.** The cell is forward. The prediction was made 2026-10-23, before the 2026-11-09 resolution. I found no retrieval of this petition's disposition and no read inside `data/qp-topics/`. Graded `not_applicable` / `retrieved_outcome_material: false`.

**Big case.** My own read is 0.15. The judicial-discipline backdrop is real, but this vehicle is a pro se collateral Tucker Act suit, disposed of below on jurisdiction in a nonprecedential order and denied without comment.
