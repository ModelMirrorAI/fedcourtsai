# Evaluation: claude-baseline

## Outcome and accuracy

This is a cert-stage arrival forecast, not a merits or interim cell. The Court granted the petition on November 13, 2026, expressly limited to Questions 1 and 2. The committed outcome labels that disposition `granted` and its route `plenary`; the limitation does not change the recorded label to `granted-in-part`. claude-baseline's `granted` prediction therefore receives **correct = 1**. With probability 0.92 and actual_granted 1, **Brier = (0.92 - 1)^2 = 0.0064**.

No cert-stage votes are scored. Judgment accuracy and semantic grading do not apply. Quantitative claims are left entirely to the harness. The stamped segment base rate, its basis, and skill score are also the harness's, not independently supplied here.

## Reasoning quality: 0.86

The rationale uses the right arrival population: its own frozen federal band under sal-v3, with no accumulated distributions, rather than a terminal no-relist slice. Its prior-Term pooling method and reported population are consistent with the historical statpack. The upward adjustment identifies concrete certworthiness considerations: an SG petition challenging invalidation of a consequential federal policy, a final appellate decision, and independently important remedial questions. It separates the judgmental uplift from measured evidence and discloses the one-sided petition record, truncation, and possible mootness.

The main weakness is the strength of several inferences. The petition says the mandate stay was **unopposed**; treating it as the appellate court's affirmative expectation of Supreme Court review overstates its signal. The assertions that percolation is impossible and that the Court takes every comparable case largely adopt the petitioner's framing rather than establish an empirical class. The discussion gives comparatively little attention to the contrary statutory reasoning. These limitations reduce the analysis grade despite the correct disposition. This grade concerns reasoning.md alone, not the structured claims or forecast document.

For base-rate use, I reconstructed the candidate-era pack with `statpack-at`: build `02dd6a20fccc232651e3e13cdea3da3066e41c5b`, digest `sha256:5b70d73d2cadac0dff2091d5aa32536fb116a3366f76592493006ca63337d0cc`. This is the inferred historical build, not a digest pinned by the candidate; no alternative build was reported. I graded the cited sal-v3 rows against that build rather than today's pack. No independently pooled scoring anchor is supplied.

## Predicted reasoning

**Grade: 0.90.** The document goes beyond predicting a grant. It calls a plenary grant in the relevant season, opposition rather than waiver, an October/November first distribution, disposition after few conferences, no CVSG, and likely pruning of Question 3 while retaining Questions 1 and 2. The staged docket confirms opposition on September 23, first distribution on October 7, conferences on November 6 and November 13, and the limited grant on the latter date. The question-selection forecast is particularly discriminating, although expressed probabilistically rather than as a firm limited-grant call. These verified procedural specifics justify a high, not perfect, grade. The record does not establish the Court's reasons for granting or any relist, so the forecast's explanation of possible relists receives no verification credit.

Future argument timing, a decision by June 2027, and the conditional merits reversal remain unresolved, not errors. The hypothetical denial writing was not tested. Neither changes the rationale grade or the mechanical claim scores.

## Leakage

The harness log records **forward** mode, August 24 calls, and full result-capture coverage. The prediction preceded the November 13 resolution. Its own-docket reading concerned the provisioned arrival snapshot; the CourtListener search concerned earlier lower-court proceedings. No query or reasoning shows this petition's eventual disposition. A logged read of an example prediction on a different docket is not evidence of outcome material for this case. Thus retrieved_outcome_material is false, influence is not_applicable, and leakage_suspected is false. The decided snapshot staged for this evaluation is not substituted for the predictor's historical inputs.

## Significance

Independent stakes assessment: **0.94**, reflecting the nationwide asylum/entry policy and the important limits on classwide relief, not agreement with the candidate's own salience number.
