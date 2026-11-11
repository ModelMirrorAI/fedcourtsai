# Evaluation — gemini-baseline

**Cell:** scotus/9026000436 (Radiall USA, Inc. v. Ramadei, No. 26-436), `evt-petition-disposition`, stage `cert`, forward. **Outcome:** denied on Nov 9, 2026, after one distribution (Oct 7, for the Nov 6 conference). Respondent had waived a response, no response was requested, there was no CVSG and no noted dissent. Two employer-side amicus briefs were filed after the predictions were made. Baseline and skill: the anchor is the stamped segment base rate (the harness pools it from the frozen `baseline` band). I quote no rate of my own. No semantic set is declared on a cert cell, and votes are not scored.

## Scores
- predicted `denied`, P(grant) = 0.02, so `correct` = 1 and Brier = (0.02 − 0)² = 0.0004.
- reasoning_quality **0.60**.

## Reasoning
The direction is right, and the main driver is right too: the vehicle is poor because of the preservation ruling below. The analysis is thin, though. It describes the Second Circuit's ground as a refusal to reach an issue "not raised at trial (which occurred before Loper Bright)". That misses the invited-error holding (Radiall proposed the motivating-factor instruction itself) and the forfeiture holding (Radiall did not raise Loper Bright in its post-trial motions, filed after Loper Bright came down). Those holdings are the strongest case for denial. gemini-baseline also seems to have worked from the questions presented and never opened the petition text or the appendix. It reads the respondent's waiver as a sign the respondent thinks the petition "frivolous", which is overstated: a waiver is the ordinary default. Its point that any grant would first need a call for a response is sound. Going below the band anchor was well judged, but it rests on fairly little analysis.

## Predicted reasoning
Grade **0.65**. The central claims were these: denial with no further relists, no CVSG, and a bare denial with no dissent. All three held. They are specific enough to have been wrong, since a call for a response was a live possibility. But they are the modal path for a baseline petition whose respondent waived, so they discriminate only modestly. The content about which questions a grant would take is conditional and unresolved.

## Leakage
Forward. The log shows only reads of the provisioned inputs (every call is `unobserved`, an engine-wide capture shape). There were no external queries and no outcome material. `not_applicable`.
