# Evaluation - gemini-baseline

**Cell:** scotus/73272491, `evt-order-call-for-response-disposition` (cert stage, response-requested moment). **Outcome:** petition denied 2026-11-16, after one post-response distribution, with no noted dissent.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.045 - 0)^2 = 0.002025.
- No vote score (cert cell). Segment base rate, skill and claim scores are the harness's and are left unset.

## Reasoning (`reasoning_quality` 0.60)

The legal analysis is sound and landed in the right place: no circuit split (conceded by the petition), an unbroken run of denials on the identical Libretti question, the restitution analogues (Hester, Rimlawi) showing no four-vote coalition, and a non-precedential summary order below. The 4.5% figure treats the call for a response as real but modest evidence, which the outcome vindicated; this was the sharpest probability of the three.

What holds the grade down is the handling of the record and of the numbers:

- It misstates the provisioned docket. It says the petition was distributed May 27 for the June 11 conference and that the case has "no amicus briefs". The docket shows two amicus briefs filed June 1 and a distribution on June 2 for the June 18 conference. The amicus support was a relevant upward signal the analysis never weighed.
- It anchors on the terminal baseline figure rather than the risk-set figure the band table designates for a band frozen at prediction, then layers on marginal paid/circuit/topic rates without a clear combination rule.
- The claim that "~92-96%" of paid criminal petitions with a waiver followed by a called-for response are denied is presented as an empirical rate with no source in the pack or the retrieval log; it is the candidate's own conclusion restated as data.
- The vehicle section predicts harmlessness and fact-bound objections the Solicitor General "will highlight"; this is reasonable speculation, labelled as such, but unverifiable here.

Net: right answer, good doctrine, well calibrated, but with record errors and an unsourced statistic doing load-bearing work.

## Predicted reasoning (`predicted_reasoning_quality` 0.75)

Central claims: denial after the BIO; resolution at the first post-response distribution in the autumn with no relist streak; no CVSG; a separate writing unlikely. All four were borne out by the docket and outcome, and the procedural-path claim was specific and made without sight of the later docket. The document loses ground for misreciting the existing docket state (wrong distribution and conference dates) and for forecasting one or two extensions where there were three - margins, not central failures. It sits at the 0.75 anchor rather than above it because the central calls, while specific, were the expected path for this posture.

## Leakage

Forward mode; the prediction (2026-10-29) predates the resolution (2026-11-16). The log's results are `outcome_only`, so calls are graded on their queries: provisioned files, statpack, corpus lookups for cited precedents and the earlier Esformes petition, one throttled CourtListener search. Nothing reaches this case's disposition. `not_applicable`.

## Big case

Own read 0.35: institutionally meaningful question (overruling Libretti), low public salience, and a routine silent denial in the event.
