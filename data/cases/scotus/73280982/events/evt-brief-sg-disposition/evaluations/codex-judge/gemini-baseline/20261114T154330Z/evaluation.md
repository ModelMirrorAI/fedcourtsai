# Evaluation — gemini-baseline

## Outcome and mechanical scores

This is a cert-stage SG-brief cell. The authoritative outcome records `granted`, binary 1, by the plenary route on November 13, 2026. The disposing entry in `record/snapshots/2026-11-14.json` limits the grant to the SG's reformulated misleading-omissions question, including the crucial phrase “additional inquiry.”

The prediction's `granted` label matches exactly: **correct = 1**. Its probability was 0.78, so **Brier = (0.78 - 1)^2 = 0.0484**. The generic outcome label matches this candidate although the docket describes the same limited grant that the other candidates encoded differently; the cell-level flag preserves that nomenclature issue without overriding the outcome. No cert votes, judgment accuracy or semantic claims are scored. Baseline, skill and mechanical claim scores are the harness's; this evaluation supplies no substitute segment rate.

## Reasoning quality — 0.82

The rationale correctly treats the invited SG/SEC recommendation as the decisive update, identifies the materiality/misleadingness distinction, explains how reformulation addresses respondents' adversity objection, and balances that against interlocutory posture, recent securities DIGs and a surviving Item 303 theory. Those are concrete certworthiness considerations grounded in the SG brief, BIO and reply, not merely a successful guess.

The main weaknesses are calibration provenance and precision. The asserted recommendation-conditioned historical frequency is not established by the supplied pack. The baseline discussion includes the case's own docket Term 2025 rather than consistently restricting the anchor to strictly earlier Terms. And grouping the First Circuit with circuits requiring a separate misleadingness inquiry overstates the SG's position: its printed page 16 says the First Circuit does not appear to require that additional showing. These limit the analysis independently of the successful outcome.

Base-rate use was checked against the reconstructed historical statpack, commit `eb6830084a187953fd58b91cb3c9125fc6775a7b`, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, not the refreshed committed pack. The rendered CVSG and individual band-row figures quoted by the candidate match that build. This historical check is not a new scoring anchor.

## Predicted reasoning

**Grade: 1.0.** The resolved central forecast was unusually specific and borne out: the reformulated first question only, plenary review, one or two further distributions, and no second CVSG. The docket shows exactly two further distributions and the matching limited grant. These were discriminating forecasts, not facts already entailed by the petition. The eventual merits result remains unresolved and earns neither credit nor penalty. The order record does not independently establish the absence of every separate writing, so that secondary expectation is not treated as verified. The grade concerns this document alone, not the probability or rationale.

## Leakage and limits

The log says forward; the October 26 prediction predates the November 13 grant. Its 56 calls have zero captured-result coverage. Their query text and the candidate's prose show no retrieval of this disposition, but unobserved results cannot be represented as failed or empty searches. The appropriate forward assessment is `not_applicable`, with no leakage exclusion. The evaluator's November 14 snapshot is post-resolution evidence and is not a reconstruction of the candidate's baseline.
