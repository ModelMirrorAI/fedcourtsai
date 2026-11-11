# Evaluation: codex-baseline

## Outcome and mechanical scores

This is a cert-arrival cell. The Court denied the petition on November 9, 2026, so the exact disposition call is correct (1). With P(any grant) = 0.008 and actual_granted = 0, the Brier score is (0.008 - 0)^2 = 0.000064. No cert-vote accuracy is scored. There is no merits judgment comparison or semantic grading on this event. Quantitative claims are left entirely to the harness; neither their probabilities nor the forecast-document grade enters reasoning_quality.

The segment baseline, skill score and baseline basis remain null for harness stamping. For assessing the rationale's use of rates, I reconstructed the candidate-time statpack with `fedcourts statpack-at`: build `2420d5dd72e1dd97585b5f0c998b82f40c3b5a32`, digest `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`, landed September 26, 2026. This is not the current checked-out pack. Its sal-v4 private-petitioner baseline reached risk set over the displayed prior Terms 2017-2025 contains 638 grant-family outcomes over a denial-reweighted denominator of 12,720, or 5.0157%. The rationale reproduces that anchor correctly and does not substitute the terminal rate or the federal-petitioner class.

## Reasoning quality

Score: **0.92**. The rationale identifies the specific jurisdictional and preservation barriers rather than relying on the eventual denial: the petition's page-7 footnote concedes that neither lower court decided the constitutional issue; its proposed Tucker Act reading must overcome the monetary-claims limitation; and a recusal theory does not itself cure the jurisdictional problem. It distinguishes the petitioner's allegations from independently established facts and separates institutional stakes from vehicle quality. The currently staged appendix, App-2 to App-3, independently confirms the jurisdictional holding and the panel's rejection of recusal, although it was fetched October 13, after this prediction. The candidate's disclosure that it lacked the appendix at prediction time is not contradicted or penalized by its availability now.

The remaining limitation is calibration: the move from an approximately 5% reference rate to 0.8% is a reasoned judgment, not a demonstrated conditional frequency. The unexplained denial is compatible with the identified barriers but does not establish the Supreme Court's reason for denying review. The score rewards the analysis, not hindsight agreement or the length of the document.

## Predicted reasoning

Score: **0.95**. The central forecast was denial after one initial distribution, without a further relist or CVSG, in November-December, and without a separate denial writing. Those procedural commitments are borne out: waiver October 16, distribution October 21 for the November 6 conference, and denial November 9. The five central claims and their record bases are set out in evaluation.json. These are meaningfully more specific than a bare prediction of denial. The denial entry supports no merits holding, and no claim about the Justices' unreported votes is inferred.

The alternative recusal question and plenary-versus-summary route were explicitly conditional on a grant that never happened. They earn neither credit nor penalty. The record cannot test what a granted case would have held.

## Leakage assessment

The harness log identifies forward mode. Its September 27 calls precede the target's November 9 resolution. I reviewed all 31 calls, including general-law searches, the corrected Testan lookup, and the two unobserved web attempts. Their queries do not seek this petition's outcome; an unobserved result is not treated as proof that a search returned nothing. The June mandamus disposition disclosed in the petition is about a different, pre-baseline proceeding. There is no evidence that the target was already decided when predicted or that outcome material shaped the forecast: influenced_prediction is not_applicable and leakage_suspected is false.

## Significance and limits

My independent stakes assessment is **0.25**: potentially consequential judicial-governance questions are embedded in a procedurally obstructed collateral suit, and this denial produces no substantive precedent. There is no missing or malformed required input and no blocker requiring a flag.
