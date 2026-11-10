# Evaluation: codex-baseline

## Outcome and mechanical score

This is a cert-stage cell. The November 9, 2026 outcome is `denied`, with `actual_granted = 0`. codex-baseline predicted `denied` at P(any grant) = 0.03: `correct = 1`; `brier_score = (0.03 - 0)^2 = 0.0009`. Cert votes are not scored, no semantic-grading block applies, and quantitative claims remain the harness's responsibility.

## Reasoning quality: 0.90

The rationale is careful about what the available record can establish. It distinguishes the October 5 sealing-motion grant from cert review, identifies the pre-docketing distribution anomaly, and avoids converting unreadable petition text into proof of no federal question or circuit conflict. It also treats apparent self-representation as an inference rather than a verdict on petition quality. A modest downward probability adjustment for waiver and limited procedural interest is explained as judgment, not a measured likelihood ratio. Denial is consistent with that analysis without proving the candidate's hypothesized reasons.

The candidate correctly distinguishes a frozen risk-set anchor from terminal-band and mixed-population cross-checks, and historical terminal associations from prospective transitions. It does not invent substantive grounds it could not read. The remaining limitations are that the analysis is primarily procedural rather than an assessment of the actual constitutional question, and the exact probability adjustment lacks an empirical calibration. Those constrain the top-end grade but do not justify punishing an acknowledged input limitation. This grade uses `reasoning.md` alone, excluding the forecast grade and any independent assessment of structured claims.

The current OCR-readable question concerns due-process sequencing of a disabled litigant's pending accommodation request before dismissal as a discovery sanction. Its recovery is dated October 18 in the current manifest, after this October 8 prediction. The current text therefore does not contradict the candidate's report of unavailable question text when it ran.

## Base-rate provenance

The comparison uses the candidate-era statpack recovered by `fedcourts statpack-at`, build `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, landed September 28, 2026; no alternative build was returned. Its `sal-v4` reached/risk-set rows support the population choice described in the rationale. The displayed terminal rates are not substitutes for that population. I do not calculate or publish another scored anchor; the harness stamps baseline, skill, and provenance using the prediction's frozen context, not the evaluator's later elevated `sal-v8` context.

## Predicted reasoning

Grade: **0.85**. The forecast specifically predicts one further distribution followed by denial in November or December, no repeated reconsideration, no CVSG, and no call for a brief in opposition after waiver. The staged docket bears out those central procedural commitments: October 14 distribution for November 6, followed by denial November 9, with no response request. This earns more than generic directional credit. The forecast does not identify a doctrinal ground, appropriately given its input limitations, and no ground is inferable from denial. The outcome confirms no noted dissent, but the broader no-explanation/no-separate-writing claim remains unresolved without a staged order or writings record. Hypothetical grant-route and question-selection content is conditional on an event that did not occur and receives neither credit nor penalty.

The cell-level ambiguity flag explains why the extra distribution is not treated as evidence of substantive relisting: the baseline appears to include a sealing-motion distribution. Observable entry counts are used without changing the outcome or scoring quantitative claims.

## Leakage and significance

The forward run occurred October 8, before the November 9 resolution. Result-capture coverage is 0.96: the petition-PDF web call is unobserved, so its null result/date cannot verify the candidate's account of getting no readable content. Its query nevertheless targets a pre-decision filing, not the disposition. The lower-court query is explicitly bounded before March 24, 2026; neither the other queries nor the prose reveals the later cert denial. Influence is `not_applicable`, and leakage is not suspected.

My independent significance assessment is **0.18**, based on the potentially recurring accommodation-sequencing question but limited demonstrated conflict and a record-specific unpublished affirmance. The candidate's abstention from its own stakes score does not affect this assessment.
