# Evaluation: codex-baseline

## Outcome and mechanical score

The event is cert-stage. The recorded October 19, 2026 disposition is `denied`, with `actual_granted = 0`. codex-baseline predicted `denied` with P(grant) = 0.16: correctness is **1**, and Brier is **(0.16 - 0)^2 = 0.0256**. The unexplained denial establishes the disposition, not the Court's reasons or its view of the underlying mandamus decision.

The prediction froze `baseline`, `sal-v4`, Term 2026, and one distribution. The evaluator's decided-docket `high` band at three distributions is not a substitute for that information state. Baseline, basis and skill are harness-owned; any comparison uses the **stamped segment base rate**. I do not pool or quote an independent rate. Votes are unscored at cert, and this event declares no semantic set. Quantitative claims and the forecast prose are outside this reasoning-quality grade.

## Reasoning quality: 0.91

The rationale carefully separates the jurisdiction to entertain mandamus from whether extraordinary relief was appropriate, and a disputed application of precedent from a clean circuit conflict. It considers the government's preservation and military-commission vehicle objections without incorrectly equating limited development below with forfeiture of subject-matter jurisdiction. Its treatment of Will's reservation is consistent with the relevant passage reproduced in the provisioned opposition at printed pages 11–12, rather than assuming that precedent conclusively resolves the petitioners' categorical theory. It also weighs the competing plea-performance accounts and the panel's treatment of Dean instead of simply counting disagreement below.

Procedural and statistical discipline are strong: the candidate distinguishes the sealing-motion grant from petition review, declines to infer case-wide recusal from a motion-specific notation, and distinguishes the United States' appellate role below from its respondent role here. Its quantitative explanation uses the frozen band and salience version, strictly prior Terms, and an explicitly described weighted calculation. More importantly, it warns that overlapping descriptive cuts cannot be multiplied and that terminal relist statistics are not incremental forward hazards. I assess the coherence of that method without independently reproducing or certifying its historical aggregate figures. It acknowledges the truncated petition, missing reply text at prediction time and limits of the appellate record.

The remaining weakness is calibration: the upward adjustment from the statistical anchor to 16% remains judgmental, and exceptional stakes and supervisory concern do not establish the size of that adjustment. Some of the precedent comparison is necessarily constrained by the incomplete record. These limits keep the grade below the top of the scale. The grade concerns only `reasoning.md`, not whether the forecast's timing, separate-writing possibilities or ancillary claims matched later events. The realized denial does not warrant reducing otherwise careful legal analysis merely because a lower grant probability achieved a smaller Brier loss.

## Leakage assessment

Frozen context and the audit log identify **forward** mode. Creation and retrieval occurred on September 18, 2026, before the October 19 denial. There are 48 calls: 46 captured and two unobserved, giving coverage approximately 0.9583. The two unobserved generic Court-rule web calls cannot independently establish failed or empty returns. Their queries do not concern the target case. Other substantive external queries concern the historical Will authority; local queries concern the provisioned record and committed aggregate statistics.

The candidate discloses filename discovery, but the logged discovery commands do not establish a read of another prediction's contents or an outcome artifact. No logged query or rationale shows this petition's already-decided outcome or post-resolution facts. I record `retrieved_outcome_material = false`, influence `not_applicable`, and `leakage_suspected = false`, without treating absent document dates or missing staged candidate flags as proof of clean retrieval.

## Stakes and input quality

The independent stakes assessment is 0.94 for capital plea enforcement in the September 11 prosecutions, executive control of bargains and prosecution-mandamus limits. The provisioned questions' CAPITAL CASE marking conflicts with the current snapshot's `bCapitalCase: false`; the cell-level flag records it. It does not justify altering the frozen band, reclassifying the case's outcome or changing the prediction.
