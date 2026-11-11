# Evaluation: claude-baseline

## Outcome and mechanical scores

This is a cert-stage distribution cell. The standard denial recorded on November 9, 2026 exactly matches `predicted_disposition = denied`, so `correct = 1`. With P(grant) = 0.004 and `actual_granted = 0`, the Brier score is `(0.004 - 0)^2 = 0.000016`.

The prediction's frozen context is October 22, Term 2026, `baseline` under `sal-v4`, one distribution and no CVSG. It is not replaced by the evaluator's later terminal context. The stamped segment base rate and skill are the harness's. Vote accuracy is omitted because this is cert, not merits. No semantic grades are written because this stage declares no semantic set and the prediction has no semantic claims. Claim scores are left to the harness.

## Rationale: 0.76

The concise rationale identifies the principal cert obstacles: an individual municipal code-enforcement dispute, summary state appellate action on an extraordinary writ, a demurrer to a seventh amended complaint, and no demonstrated interjurisdictional split. It sensibly distinguishes a claimed conflict among this Court's own precedents from competing lower-court holdings. It also notices the missing waiver entry rather than claiming an express waiver. These points give a defensible qualitative basis for a very low grant probability.

There are meaningful limitations. The proposition that the case is interlocutory and likely controlled by state procedural grounds is more categorical than the incomplete trial-court text warrants; it would be stronger framed as vehicle risk. The rationale supplies no identified empirical source for its statement about self-represented paid-petition grant rates. It also misdescribes the relist-zero terminal group as petitions that ended "undistributed": a petition considered at its first distribution can have zero relists. The cited granted-only relist figure is not the whole grant-family probability, which also includes GVR. These do not reverse the denial analysis, but they weaken the precision of its statistical explanation.

I checked base-rate use against reconstructed build `eb6830084a187953fd58b91cb3c9125fc6775a7b`, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`. No alternative build was returned. The historical sal-v4 reached-band table supports the rationale's strictly prior-Term anchoring direction; there is no penalty for using the pack available at prediction rather than a later refreshed pack. The terminal/risk-set and grant-family qualifications above concern its interpretation, not a comparison with a newer numerical baseline. I supply no independently pooled baseline.

The unexplained denial supports the prediction but does not establish the Court's reasons. This rationale grade is separate from the forecast-document assessment and does not reward length or mere correctness.

## Predicted reasoning: 0.90

The central calls were denial by a plain order entry, no further distribution after the first conference, and no CVSG. They are specific and borne out. The opening phrase "at the November 6 conference" is read in its procedural context as first-conference resolution, not as claiming the public docket entry would necessarily be dated November 6; the recorded public disposition was November 9. No calendar error is manufactured from that shorthand.

The outcome explicitly confirms no noted dissent. It does not independently settle every possible separate statement or an unrecorded response request; those assertions are marked unresolved, not guessed or treated as misses. The conditional reformulation of the questions and conditional summary route earn neither credit nor penalty because review was denied. The forecast earns its grade from the observed procedural trajectory, independently of weaknesses in `reasoning.md`.

## Leakage

The harness log records forward mode and eight calls with captured results. All occurred on October 22, before the November 9 resolution. Queries read the then-provisioned snapshot and filings, the statpack, schemas and a formatting example; there is no external retrieval of this petition's outcome. Neither prose document presupposes a resolved Supreme Court petition. The evaluator's own resolved snapshot does not imply it was the candidate's input.

Accordingly, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. Captured null document dates are considered alongside the queries and prose, not used alone as proof of clean retrieval. No additional case facts were retrieved for grading.

## Significance and limits

My independent stakes assessment is 0.12. Residential privacy has potential broader relevance, but the concrete petition is an individual local dispute with a weak appellate vehicle and no demonstrated appellate split. This is not an agreement calculation using the candidate's score. There is no evaluation blocker.
