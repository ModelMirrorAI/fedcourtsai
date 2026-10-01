# Evaluation: gemini-baseline

## Outcome and arithmetic

This is an interim application to vacate an execution stay. The supplied outcome records `granted`, `actual_granted: 1`, resolved September 30, 2026. gemini-baseline predicted `granted` with probability 0.90: **correct = 1**, **Brier = (0.90 - 1)^2 = 0.01**. This is the lowest realized Brier loss among these three candidates, but one realized outcome cannot establish calibration or the superiority of the analysis.

## Reasoning quality: 0.64

The rationale correctly identifies the direction of relief and the relevant distinction between the overall interim population and a State request to lift an execution stay. Its emphasis on lateness and the successive-petition issue has an identifiable basis in the provisioned application, which describes the timing, quotes the circuit dissent, and advances those arguments. The prior-Term arithmetic is also consistent with the committed table.

The jump to 90% is insufficiently justified, however. The asserted historical pattern is not quantified or supported by a successful, observable analogue query. The analysis treats the applicant's characterization of the Rule 60(b) motion as nearly dispositive without meaningfully testing whether the alleged defect concerns the integrity of the earlier proceedings. It does not engage the independent-prejudice ground in detail, address the irreversible-harm argument, or develop the procedural possibility that lower-court action changes the application before disposition. Its stated uncertainty is largely whether a subset of Justices persuades the majority. That is a narrower uncertainty account than the contested record warrants. These are shortcomings of analytical support and balance, not penalties for brevity or for making a confident forecast that happened to win.

The outcome does not supply the Court's rationale, so the grant cannot verify the candidate's asserted doctrinal explanation. `reasoning_quality` grades only `reasoning.md`; the forecast document and procedural claim probabilities are not separately scored here or folded into it.

## Baseline and scoring boundaries

On this interim event, baseline and skill belong to the harness and are omitted. The prediction's frozen application Term is 2026. The committed interim table's preceding 2024–2025 rows contribute 31 grants over 296 resolved substantive cases, exceeding the 50-case floor; earlier displayed prior Terms contribute no resolved cases. This is committed-pack context, not a claim about current corpus state; no corpus vintage was obtained. The baseline is conditioned on machine-matchable resolution, counts withdrawn/dismissed cases as ungranted and mixed dispositions denial-first, combines unevenly parsed Terms, and covers a broader population than the escalation-selected forecast set. It does not calibrate State capital-stay vacatur applications specifically or establish forecast skill. The harness has not yet stamped this evaluation.

`base_rate_basis` remains null. Interim votes are unscored, no merits semantic set is declared, and mechanical claim scores are harness-owned. Those fields are absent.

## Leakage assessment

The log states forward mode, but all 23 call results are unobserved. The query strings show provisioned-file and statpack reads and two corpus-query attempts. The retrieval note reports the vacate-stay command failed; this is a self-report, not captured evidence of failure. The earlier unrestricted applications query is not covered by that note, and its result is also unavailable. Therefore `retrieved_outcome_material` is null, not false: actual exposure cannot be established from the observed record.

Neither visible query intent nor the rationale specifically seeks or presupposes this application's completed disposition. The dissent discussed in the rationale is described in the provisioned application and is not itself evidence of outside outcome retrieval. Zero capture coverage is a telemetry limitation, not a defect or a basis by itself to suspect influence. The same-day prediction and date-only resolution leave exact ordering uncertain but do not prove that a decided case was provisioned forward. I retain the forward `not_applicable` influence assessment and `leakage_suspected: false`, explicitly not a finding that every unseen response was clean.
