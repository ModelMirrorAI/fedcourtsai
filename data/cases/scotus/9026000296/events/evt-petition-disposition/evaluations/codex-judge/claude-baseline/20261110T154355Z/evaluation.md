# Evaluation: claude-baseline

## Outcome and scoring

This is a cert-stage cell. The terminal snapshot records one distribution for the November 6, 2026 conference and a denial on November 9, 2026. The outcome is `denied`, with `actual_granted = 0`. claude-baseline predicted `denied`: `correct = 1`; Brier = `(0.012 - 0)^2 = 0.000144`.

Vote accuracy is omitted because cert votes are never scored. There is no merits judgment or semantic-claims block to grade. Quantitative claim scores are left to the harness. The frozen context carries baseline/sal-v4, so the harness selects the risk-set anchor; all baseline and skill calculations are left to the stamp. Any skill comparison is against the stamped segment base rate, not an independently supplied anchor.

## Reasoning quality: 0.78

The rationale identifies the procedural notice issue under Ruffalo and FRAP 46/47, distinguishes it from the conceded filing errors, and explains why a single-attorney, record-intensive dispute may fail to attract review. The response waiver, absence of a response request, and routine first distribution are accurately described in the staged docket. Appendix pp. 22a–27a substantiate the concern about the disciplinary response and later corrections becoming additional candor grounds. These are relevant reasons for a low grant forecast, not merely a retrospective appeal to the eventual denial.

The analysis is less complete on the competing reading of the charging order. Appendix pp. 29a–32a already identify fabricated authorities, attempted corrections, candor obligations, possible suspension and an available hearing. The rationale expressly admits that it did not independently compare that notice with the final findings. Its waiver-based downward adjustment is qualitative rather than calibrated, and equating a relist probability roughly with a response-request probability conflates distinct procedural possibilities. The petition discusses a broader, imperfect disagreement over evidentiary burdens, although no square conflict on these QPs is established. The unexplained denial does not establish which of these reasons motivated the Court.

I checked base-rate use against the prediction-era artifact reconstructed by `statpack-at`: build `886549a3ac32bdba039691b6d2ca7dc57bb72561`, digest `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, with no alternative build returned. Its prior-Term sal-v4 risk-set data support the candidate's approximate historical anchor; the rounded numerator is immaterial. This historical check is not a second scored baseline.

## Predicted reasoning: 0.85

The central testable commitments are denial following the first scheduled conference, no additional distribution, and no CVSG. Each is borne out by the terminal docket and outcome. The timing and no-relist call add discriminating procedural content beyond a generic prediction that cert will be denied, warranting a grade above the generic anchor.

The conditional QP 1/Ruffalo and summary-correction branches were not reached and earn neither credit nor penalty. The outcome records no noted dissent, but the absence of a complete order or writings inventory leaves the broader prediction of no separate statement unresolved. No internal vote count or reason for denial is inferred. The document does not earn the top anchor because much of its proposed doctrinal content remains untested and the denial itself gives no supporting rationale.

## Leakage

The harness log records forward mode, seven calls and captured-result coverage of 1.0. Its queries show local reads of the provisioned record and committed statpack, plus output writing. Captured digests are not substitutes for result bodies, but there is no case-outcome query or disclosure of an already-resolved petition. The October 15 forecast precedes the November 9 disposition. Forward influence is `not_applicable`, retrieved outcome material is false, and leakage is not suspected.

## Stakes

My independent stakes assessment is 0.18: recurring disciplinary-process and technology-disclosure concerns, but a narrow record and no new Supreme Court holding. This is not an agreement score with the candidate's assessment.
