# Evaluation: claude-baseline

## Outcome and scores

This is a **cert** cell. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. claude-baseline predicted `denied`, so exact-label correctness is **1**. Its grant probability was **0.005**; the Brier score is `(0.005 - 0)^2 = 0.000025`.

The candidate's frozen context supplies **baseline / sal-v4 / Term 2025**. The matching committed `metrics/statpack.md` table renders all 10 of its 10 Terms. I pool only the bracketed baseline-band reached figures for **2017–2024**, excluding 2025 and 2026. The rate/denominator pairs, newest first, are 5.7%/1,271; 5.9%/1,312; 5.8%/1,192; 5.6%/1,500; 4.5%/1,739; 4.6%/1,399; 4.6%/1,524; and 4.7%/1,643. Their resolved-weighted rate is **592.925 / 11,580 = 0.05120250431778929**, on the **risk_set** basis. The numerator is reconstructed from rounded published percentages, not an exact observed grant count. Brier skill is **0.9904641896985705**. There is no rendered-window truncation or salience-version mismatch.

These are the committed pack's live/historical-slice, denial-reweighted estimates, not a fresh corpus query. The frozen prediction snapshot is dated September 16, 2026; no claim is made about current corpus freshness. A low Brier score on this one denial does not establish general calibration.

## Reasoning quality: 0.82

The rationale correctly starts from the frozen reached-band population and then offers case-specific reasons to move below it: the response waiver, lack of a developed conflict in the supplied petition, deferential review of factual findings, and a fact-bound vehicle. The provisioned appellate appendix, pages 13a–15a, supports the central characterization: it applies deferential review even to documentary inferences while reserving legal questions for de novo review. The rationale identifies document truncation and the possibility of later docket activity instead of presenting its record as exhaustive.

The main weaknesses are overstatement and an incompletely supported numerical adjustment. A government waiver does not itself show that no Justice's chambers has identified interest. The assertions that appellate courts uniformly agree and that no possible grant channel is plausibly open exceed the demonstrated search and record. Describing the risk-set average as a floor is also imprecise: it is an average from which a justified case-specific forecast may depart. The rationale does not quantitatively establish why the appropriate residual is 0.5% rather than another small probability. Its analysis remains substantially grounded despite these limitations.

The denial is consistent with the forecast but does not establish that the Court adopted these reasons. This score assesses the analysis in `reasoning.md`, not the forecast document, the success of individual procedural claims, or the smaller Brier error relative to other candidates.

## Leakage and scoring boundaries

The captured log identifies **forward** mode. The prediction and calls are dated September 17, before the October 5 resolution; coverage is **28/28 captured calls**. The general corpus query's September 17 document date and the own-docket metadata lookup's May 19 date do not disclose this petition's eventual disposition. The candidate reports that the lookup found a pending docket. Its contemporaneous reasoning treats denial as a forecast, not a known result.

One captured shell call also reads a prediction file selected across case directories. Only its masked query and result digest are available, so I do not infer whose record it was or what it contained. That traversal does not, on the available evidence, establish retrieval of this case's outcome. The assessment is `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.

Cert votes are not scored. No judgment comparison or semantic grades apply. Quantitative claim scores and provenance stamps remain the harness's responsibility. The forecast document was read only for context. No independent big-case score is supplied.
