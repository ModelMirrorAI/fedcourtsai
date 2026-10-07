# Evaluation: claude-baseline

## Outcome and numerical score

The cert-stage outcome records denied on October 5, 2026, with actual_granted = 0. The candidate's denied label is correct. P(any grant) = 0.005 yields Brier = 0.000025.

The prediction's own frozen context supplies baseline, sal-v4, and Term 2026. The matching metrics/statpack.md band table supports risk_set scoring. The bracketed reached percentages for all displayed prior Terms, 2017–2025, pool to 637.385 / 12,720 = 0.05010888364779874. The numerator is a reconstruction from rounded rendered percentages, not an integer count; this precision is consistent with the candidate's approximately 5% anchor. No terminal rate or evaluator-side band is substituted. The table shows all 10 pack Terms, with 2026 excluded, so there is no window-divergence flag. Skill = 1 - 0.000025 / baseline^2 = 0.9900434116032965. This uses the committed pack, not a refreshed corpus.

## Reasoning quality: 0.85

The rationale explicitly chooses the correct versioned risk-set anchor and prior-Term window. It connects the downward adjustment to the memorandum decision, disputed preservation and record questions, lack of a demonstrated conflict, and the limits of the petition as a vehicle. It identifies the adequate-state-ground contention as the strongest possible hook instead of treating the family-law label as dispositive. Its disclosure that the lower-court decision was available only through the petitioner's characterization is useful, as is its acknowledgment that the strong adjustment could be overconfident.

Several propositions exceed the supporting evidence. Assertions about self-represented paid petitions granting at a small fraction of the counseled rate are not backed by a cited subgroup estimate. Thirty Arizona denials are a small selected comparison, not a precise probability for this petition. Absence of a response request in the snapshot is not verified absence from a current docket, and the statement that no intervening decision exists is stronger than the reported search coverage supports. The closing timing description also blurs an October 4 snapshot label with the day after a September 28 conference; October 4 is six days later. These limitations reduce analytical confidence without making the denial forecast unsound. A proper scoring rule does not itself determine the residual probability to retain.

## Leakage and scope

All logged calls occur October 4, before the recorded October 5 denial. Capture coverage is 1.0. Four CourtListener searches concern this case or the underlying decision; the candidate reports zero results. The general corpus query has a retrieved document date of October 2 and is described as returning other, mostly emergency, cases. That date predates this event's resolution and is not evidence of this petition's outcome. No logged date or passage in the rationale shows an already-decided petition. Forward retrieval was permitted; influence is not_applicable and leakage_suspected is false. Digests and capture markers are not substitutes for unseen full result bodies.

The forecast was read but not scored, and the structured claims and their discussion were not used to grade claim accuracy or adjust reasoning_quality. Claim scores remain the harness's. Cert votes and semantic propositions are not scored. The optional big-case assessment is omitted because candidate significance judgments were visible before an independent assessment was formed.
