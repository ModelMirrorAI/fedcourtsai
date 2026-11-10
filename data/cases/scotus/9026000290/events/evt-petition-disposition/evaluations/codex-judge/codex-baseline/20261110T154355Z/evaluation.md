# Evaluation: codex-baseline

## Outcome and mechanical scores

This is a cert-stage distribution cell, not merits or interim. The recorded outcome is a standard denial on November 9, 2026. The prediction named `denied`, so `correct = 1`. With P(grant) = 0.004 and `actual_granted = 0`, the Brier score is `(0.004 - 0)^2 = 0.000016`.

The prediction froze `baseline`, `sal-v4`, Term 2026, one distribution and no CVSG on October 22, 2026. The evaluator's later `sal-v8` context does not replace that information set. The stamped segment base rate and skill are the harness's, not independently supplied here. Vote accuracy is omitted because cert votes are not scored. No semantic grade block is written: this stage declares no semantic set and the prediction has no semantic claims. Mechanical claim scores are left to the harness.

## Rationale: 0.92

The rationale makes a strong, record-sensitive case for denial rather than simply inferring correctness from the eventual result. It identifies the absence of a demonstrated interjurisdictional split, the summary state writ posture, the sprawling allegations and the difficulty isolating a clean dispositive federal issue. It correctly treats the trial-court appendix as incomplete: the staged text supplies a cover page and a Clerk's Office notice, not the substantive demurrer reasoning. It describes finality as a risk rather than claiming to have established an absolute jurisdictional bar. The distinction between an unrecorded response and a proven waiver is also careful.

I checked its base-rate use against the historically reconstructed statpack, build `eb6830084a187953fd58b91cb3c9125fc6775a7b`, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, not against a later refreshed pack. `statpack-at` found no alternative build. The cited sal-v4 reached-band population and strictly prior-Term selection fit that build, and the rationale keeps terminal relist/CVSG cuts separate from prospective hazards. I do not supply a second numerical baseline. The precise reduction to a very small grant probability and the conditional summary-route probability remain judgmental rather than empirically calibrated; the rationale candidly acknowledges that limitation.

The unexplained denial does not establish that the Court adopted any of these legal reasons. This grade concerns the soundness and evidentiary discipline of `reasoning.md`, independently of the forecast-document grade.

## Predicted reasoning: 0.90

The central commitments were ordinary denial, no additional distribution, no CVSG, and disposition soon after the November 6 conference. Those are more specific than merely predicting denial and are borne out by the single-distribution outcome and November 9 docket entry. The conditional question selection and plenary-versus-summary discussion are neither rewarded nor penalized because review was never granted.

The outcome confirms no noted dissent from denial. It does not separately establish the broader absence of every statement respecting denial, so that combined claim is marked unresolved rather than guessed or counted as a miss. The grade rests on the specific procedural trajectory that the staged record actually resolves, not on private votes or an inferred merits holding.

## Leakage

The captured log identifies a forward prediction made on October 22, before the November 9 resolution. I reviewed all 31 call queries; 29 have captured results. The local reads concern the then-provisioned snapshot and filings or administrative/statpack inputs. The two uncaptured web queries concern general Rule 10 material, not this case's result. I do not treat their null document dates as proof that nothing returned. Neither the queries nor either prose document reveals this petition's eventual disposition. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.

The evaluator's resolved November 9 snapshot is evidence for this evaluation, not evidence that the candidate saw a decided case. No additional case facts were retrieved for grading.

## Significance and limits

My independent stakes assessment is 0.12: the questions invoke potentially broad residential-privacy principles, but this vehicle is a local individual enforcement dispute with summary state appellate treatment and no demonstrated appellate split. This is not an agreement score against the candidate's stakes number. There is no evaluation blocker.
