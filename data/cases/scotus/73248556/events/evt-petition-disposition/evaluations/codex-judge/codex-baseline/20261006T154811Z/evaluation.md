# Evaluation: codex-baseline

## Outcome and numerical scores

This event resolves on the cert axis: the supplied outcome is `denied`, dated October 5, 2026, with grant indicator 0. codex-baseline also calls `denied`, so exact-label correctness is **1**. P(any grant) = 0.18 yields **Brier = (0.18 - 0)^2 = 0.0324**. Its larger residual grant probability incurs more loss on this denial, but does not by itself make its analysis unsound.

The frozen prediction context supplies federal band under sal-v4 and docket Term 2025. The matching committed statpack's federal `reached` percentages and weighted denominators for 2017–2024 are, respectively: 76.5%/17, 43.5%/23, 88.5%/26, 65.9%/41, 72.7%/11, 89.5%/19, 86.2%/29, and 60.0%/15. Pooling those displayed strictly-prior rows gives **132.039/181 = 0.7294972375690608** with `risk_set` basis. The numerator is implied by rounded displayed rates, not an exact count. Skill is **1 - 0.0324 / 0.7294972375690608^2 = 0.9391167668945966**.

All 10 of the pack's 10 Terms are rendered; 2025 and 2026 are excluded from the pool. No version mismatch or truncated display requires omission or a flag. The statpack header supplies no corpus-wide pull vintage, so these numbers describe the committed table available here rather than a freshly queried remote. The evaluator performed no live corpus query. This single-cell skill is not a general performance or calibration claim.

## Reasoning quality: 0.92

The rationale is careful about both legal posture and evidentiary limits. It distinguishes the contingent GVR request from a plenary challenge, identifies the lower court's reliance on the companion line of reasoning, and explains why an adverse lead decision can reduce rather than mechanically eliminate remand probability. It explicitly treats the opposition's account as an adversarial representation, not independently verified Supreme Court reasoning, and treats comparator cert denials as predictive context rather than merits precedent. The petition's stated request and the opposition's substantive discussion support those distinctions.

Its statistical explanation uses the correct frozen federal population and strictly-prior Term pool, rather than substituting the much lower private-petition rate. It also distinguishes terminal relist descriptions from prospective transition probabilities. The summer interval and a concurring judge's discussion are not inflated into relists or a panel dissent. Uncertainty from unavailable companion opinion text is clearly stated, and the remaining GVR probability is explained as a judgment rather than a fitted estimate.

Limitations remain: the decisive reading of the intervening decision largely depends on one side's filing, and the precise adjustment from roughly 73% to 18% is not empirically calibrated. More direct engagement with the complete companion opinion could materially change that estimate. These reservations prevent a perfect score but do not justify treating the eventual denial as proof that the residual probability was unreasonable. The recorded denial also does not confirm any particular doctrinal account of the Court's decision.

Only `reasoning.md` is graded qualitatively. The forecast document and structured quantitative claims are not folded into this score. Cert votes and semantic propositions are not scored; mechanical claims remain the harness's responsibility.

## Leakage

The frozen context and log identify a forward prediction made September 16, before the October 5 resolution. Its external queries concern Hemani, not Hembree's eventual disposition. The rationale discloses the companion material's role and its limited verification. Such earlier companion context is permissible in forward mode.

The log contains 26 calls: 23 captured and three unobserved web calls, for coverage 0.8846153846153846. Although the retrieval note describes those web attempts as yielding no usable content, the unobserved markers do not independently establish empty results. I assess them from their Hemani-specific query and PDF paths. The generic `other` call class is not itself suspicious. A filesystem instruction search explicitly excludes the labeling-artifact path; it is not evidence of reading those artifacts. Nothing in the visible queries or prose indicates an already-decided Hembree petition. Accordingly, outcome material is not shown, influence is `not_applicable`, and leakage suspicion is false.
