# Evaluation — claude-baseline

## Outcome and mechanical scores

This is a cert-stage SG-brief cell. The authoritative outcome is `granted`, binary 1, by the plenary route on November 13, 2026. The docket grants review limited to the SG's reformulated first question. The candidate calls precisely that limited review `granted-in-part`, so **correct = 0** under the required exact-label test. This is a label mismatch, not an erroneous substantive prediction about the grant's scope. With probability 0.80, **Brier = (0.80 - 1)^2 = 0.04**. A cell-level flag records the label ambiguity without replacing the authoritative outcome.

No votes, merits judgment comparison or semantic grades are scored on this cert event. The segment base rate, skill and mechanical claim scores are left to the harness; no competing numerical anchor is supplied.

## Reasoning quality — 0.85

The rationale correctly centers the SG/SEC recommendation to grant the first question, identifies the additional-inquiry reformulation as the response to an adversity problem, and recognizes why the second question is a poor vehicle. It explains upward adjustments for a recurring legal question and downward adjustments for interlocutory posture and incomplete adversity, rather than treating favorable merits arguments as sufficient by themselves. Its prior-Term risk-set framing is appropriate, and it clearly distinguishes the committed pack from background knowledge about SG recommendation effects.

The principal limitations are the unsupported precision of the recommendation-conditioned frequency and a compressed treatment of the circuit disagreement. The SG describes the Second Circuit's position as less clear and only apparently conflicting; the candidate states the conflict more categorically. The suggestion that most SG recommendations are denials is not established by the pack's outcome-only CVSG table. These are evidentiary and legal-calibration weaknesses, not consequences of its structured label or of the forecast document.

Base-rate use was checked against historical statpack commit `eb6830084a187953fd58b91cb3c9125fc6775a7b`, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, reconstructed for this run rather than against today's refreshed pack. Its rendered CVSG and prior-Term high-band figures are consistent with that build. This check does not replace the stamped segment base rate. The candidate reports an earlier bad questions extraction; the evaluator's current file contains both questions, so that historical defect cannot be independently established here.

## Predicted reasoning

**Grade: 1.0.** The specific cert-stage core held up: Question 1 only in the SG's reformulated terms, plenary review, a November conference after redistribution, a grant by the second post-CVSG conference, and no further CVSG. The October 21 and November 9 distributions and November 13 grant support that path. Although the candidate did not make a relist its modal path, it expressly allowed one before the second conference. No central resolved claim failed. The anticipated merits ground and spring 2027 argument timing are not yet resolved and receive neither credit nor penalty; the alternative denial-writing discussion is likewise untested. An accurate prose forecast does not change the exact-label mechanical result.

## Leakage

The prediction was forward on October 26, before the November 13 disposition. All 11 logged calls carry captured results and their queries concern the provisioned October 7 record, pre-decision documents, metrics, instructions or output creation. No outcome-seeking query or result-presupposing prose appears. There is no evidence of target-outcome retrieval; influence is `not_applicable` and no leakage exclusion applies. The candidate's own October 7 baseline is not confused with the evaluator's November 14 snapshot.
