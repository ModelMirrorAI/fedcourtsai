# Evaluation: codex-baseline

## Outcome and mechanical scores

This is a cert-stage arrival forecast. The petition was denied on November 9, 2026: `actual_disposition = denied`, `actual_granted = 0`. codex-baseline predicted denial with P(any grant) = 0.03. Exact-label correctness is **1** and the Brier score is **0.0009**: `(0.03 - 0)^2`.

The docket records a September 18 response waiver, one distribution on October 14 for the November 6 conference, and denial on November 9. The outcome records one distribution, no CVSG date, and no noted dissent from denial. These observations do not explain the Justices' reasons for declining review. Votes are not scored at cert, and no merits semantic block is applicable. Quantitative claims are left to the harness. The segment baseline, its basis and Brier skill are also left to the harness; any comparison is to the stamped segment base rate, not an independently supplied anchor.

## Reasoning quality: 0.90

The rationale distinguishes a plausible notice objection from a demonstrated certworthy conflict. It identifies the petition's Ruffalo theory, the original warning of suspension or disbarment, the lack of a requested hearing on the noticed charges, and the competing characterization of later statements as aggravation or evidence of existing candor violations. It also recognizes that the Rule 47(b) theory depends on treating the decision as imposing a new source-disclosure requirement rather than enforcing existing candor duties. The staged petition and appendix support these as genuine competing characterizations; denial does not adjudicate between them.

The analysis is unusually careful about what it actually inspected. Its statements that no separately provisioned appendix or opposition was then available describe its prediction-time record, not a defect inferred from the fuller record provided to this evaluation. It treats the petition's account as advocacy, not independent factfinding, and identifies its incomplete underlying-record access. It does not treat zero distributions at arrival or the initial absence of an opposition as adverse signals. The lower confidence in review follows from a fact-sensitive vehicle and an imperfectly aligned split, rather than from AI novelty alone.

Base-rate use was checked against the reconstructed prediction-time statpack, build `2420d5dd72e1dd97585b5f0c998b82f40c3b5a32`, digest `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`, recovered with `statpack-at`. Its selection of the private baseline risk set and strictly-prior OT2017–OT2025 rows matches that build. Its pooling of rounded Markdown percentages is explicitly approximate. The remaining limitation is that the exact downward adjustment is judgmental, not supported by a discipline-specific reference class. The score grades this rationale only, independently of the forecast document and structured claims.

## Predicted reasoning

**Grade: 0.90.** The central unconditional calls were denial, an initial distribution followed by no additional relist, and no CVSG. All match the staged outcome and docket. The explicit distinction between a first distribution and an additional conference made this more discriminating than a generic denial forecast. It did not specify the actual conference date or response route as precisely as a fully detailed procedural forecast might.

The no-noted-dissent component is supported by the outcome. The broader no-separate-statement prediction remains unresolved because the record does not carry the disposing order's full text or a complete denial-writing inventory. This is not scored as a miss. The first-question focus, summary-versus-plenary route and doctrinal ground were conditioned on a grant that never occurred; they earn neither credit nor penalty. None of those conditional passages enters reasoning quality.

## Leakage assessment

The captured log labels the prediction forward, and its September 27 calls precede the November 9 resolution. It contains provisioned-file reads, statpack work, general rules searches and historical Ruffalo lookups, not retrieval of this petition's disposition. Captured-result coverage is 0.9375 across 32 calls. The two unobserved web calls cannot be credited as empty from their missing dates or digests, but their visible queries target general procedural rules and do not suggest outcome retrieval. The reasoning contains no already-decided signal. Accordingly, `retrieved_outcome_material = false`, influence is `not_applicable`, and leakage is not suspected.

## Case significance

My independent significance assessment is **0.25**. Fair notice in federal discipline and source disclosure when correcting fabricated authorities have recurring professional importance, but this vehicle concerns an individual suspension and produced no Supreme Court merits ruling. This assessment is the same for every candidate and is not an agreement score.
