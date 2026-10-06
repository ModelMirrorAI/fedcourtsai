# Evaluation: codex-baseline

## Outcome and quantitative scores

The recorded October 5, 2026 outcome is `gvr`, with `actual_granted = 1`. The provisioned docket states that the judgment was vacated and remanded for reconsideration in light of Louisiana v. Callais. codex-baseline predicted `gvr` with P(any grant) = 0.84: **correct = 1**, **Brier = 0.0256**. Against the shared prior-Term risk-set baseline, **Brier skill = 0.9394705197973353**, using 1 − 0.0256 / (0.34966592427616927 − 1)². This strong single-event score does not establish calibration across events.

## Reasoning quality: 0.88

The rationale is careful about the object of review: the petition challenges a mootness judgment, not a merits determination of unconstitutional racial predominance. It distinguishes petitioner's advocacy from adjudicated facts and the earlier 2024 remand from the outcome being forecast. Those distinctions are supported by the supplied petition and questions presented. It also correctly separates interrupted distributions from substantive relists and uses the frozen salience band rather than recalculating one from the decided docket.

Its baseline is reproducible: the eight strictly prior rendered Terms and unrounded risk-set fields reproduce 314 / 898. The upward adjustment identifies the State's reported remand request and the intervening-precedent mechanism, while explaining that a GVR does not establish a constitutional violation. It confronts the State's alternative mootness arguments and the contingency that related litigation might be handled without reopening this judgment. A coherent allocation across grant and non-grant routes makes clear that 0.84 is not a probability of plenary review.

The principal limitation is the size of that adjustment. Recognizing a conditional GVR request does not itself quantify the likelihood that its condition will be satisfied. The rationale has less independent investigation of companion-case obstacles than its high 0.84 headline might warrant, and its allocation remains judgmental rather than estimated from analogous cases. The documented retrieval identifies the June briefs, but their full text is not reproduced in the staged transcript; this evaluation does not independently verify every account of those arguments. The correct disposition supports the proposed mechanism without retroactively proving the ex ante confidence was calibrated. The quality score is separate from the favorable Brier result and from the unscored forecast and claim block.

## Leakage

The candidate's log records `forward`, with 34 calls on September 16, 2026, before the October 5 disposition. Thirty-two calls are marked captured; two browser rows are unobserved. Those two rows identify the exact June 2 respondent PDF and June 10 reply PDF, not searches for subsequent history. Captured command metadata then shows extraction of those dated filings through the shell. The candidate's assertion that the browser attempts yielded no usable text cannot itself be confirmed from unobserved rows; neither null dates nor the collapsed `other` tool class establishes what a result contained.

The trace and rationale reveal no search for or use of this petition's eventual disposition. The earlier remand and the June filings' descriptions of intervening precedent are pre-resolution context, not the October outcome. Assessment: `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. The ordinary forward information boundary, not the evaluator's terminal snapshot, governs this assessment.

## Baseline and scoring scope

All baseline choices use this candidate's frozen context: Term 2025, band `high`, salience version `sal-v4`. The matching `metrics/statpack.md` heading and bracketed reached figures define the `risk_set` population. The table renders all 10 of its 10 Terms; only the eight strictly earlier rows, OT2017–OT2024, enter this evaluation. OT2025 and OT2026 are excluded. The corresponding unrounded `prefix_est_grant_rate` and `prefix_weighted_resolved` values in `metrics/statpack.json` give 314 / 898 = **0.34966592427616927**. This is a denial-reweighted paid-segment estimate, not an unconditional cert rate. There is no rendered-window truncation or salience-version mismatch to flag.

These are committed-pack figures, not a refreshed remote-corpus claim: no corpus blob, corpus-wide freshness stamp, or case `last_pulled` was consulted. Case evidence is the provisioned October 5, 2026 snapshot and recorded outcome; prediction timing comes from the candidate's own September 16 context and captured log. The evaluator's terminal context was not substituted for the prediction's frozen context.

This is a cert cell. Votes, merits judgment accuracy, and semantic grades are not scored. The forecast document was read only for context; neither it nor the quantitative claims contributes a separate grade or enters reasoning quality. Claim scores and provenance stamps are left to the harness. The GVR establishes the disposition, not an adjudication endorsing every argument in the petition.
