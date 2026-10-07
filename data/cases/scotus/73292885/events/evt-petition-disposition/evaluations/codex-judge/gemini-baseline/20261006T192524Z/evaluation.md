# Evaluation: gemini-baseline

## Outcome and numerical score

This is a cert-stage event. The supplied outcome records denial on October 5, 2026, with actual_granted = 0. The candidate predicted denied with P(any grant) = 0.01: correct = 1 and Brier = (0.01 - 0)^2 = 0.0001. The provisioned October 5 snapshot also records the denial; it is evaluation evidence, not the candidate's September baseline.

The prediction freezes baseline under sal-v4 and Term 2025. The matching committed statpack table supplies the risk-set baseline, using its bracketed reached rates rather than terminal-band rates. Pooling displayed Terms 2017–2024 gives a weighted resolved denominator of 11,580 and a numerator of 592.925 from the rounded displayed percentages: baseline = 0.05120250431778929. Terms 2025 and 2026 are excluded. The caption renders all 10 of 10 Terms, so there is no rendered-window shortfall. Skill = 1 - 0.0001 / baseline^2 = 0.961856758794282. This is a denial-reweighted estimate from the committed pack, not a fresh corpus query; rounding limits its precision. A favorable single-event score is not evidence of cohort calibration.

## Reasoning quality: 0.68

The rationale identifies the low-signal first-distribution posture, uses an approximately appropriate prior-Term reached-band anchor, and explains why a fact-specific private protection-order dispute is a weak vehicle despite broadly framed constitutional questions. It acknowledges the unavailable opposition and retains some uncertainty about a narrower issue. Those are useful reasons for a low grant probability, independently of the realized denial.

The analysis is nevertheless thin. It does not show the pooled calculation or identify a specific preservation, conflict, or vehicle defect from the underlying decisions. Calling the petition a personal grievance and relying on pro se status does not substitute for examining its procedural and constitutional theories. The move from roughly 5–6% to 1% is judgmental and only loosely justified; generalized historical-practice assertions are not supported by a matched comparison set. The denial does not establish that these characterizations were the Court's reasons.

Only reasoning.md is graded. The forecast document was read for context but is not scored; neither auxiliary quantitative claims nor their eventual accuracy enter this grade. Cert votes and semantic claims are not scored. The optional independent stakes assessment is omitted.

## Leakage and data limitations

The captured call timeline is September 16, before the October 5 resolution, and the log marks forward mode. No query or prose passage shows this petition's disposition as already known. Outcome material is assessed false and influence not_applicable, with leakage_suspected false. Capture coverage is 0.0: every result is unobserved, so missing result dates are not evidence of failed or empty retrieval. This assessment rests on the timing, queries, and reasoning, not on proof of what every response contained.

The retrieval note reports that looking up docket 73292885 returned an unrelated Meidinger tax case. The staged log confirms a lookup was attempted but does not expose its response; flags.json preserves this as an unverified identifier-quality report for follow-up. I did not repeat that lookup or substitute its reported facts for the provisioned case.

The candidate reports empty opposition text at prediction time. The evaluator's current document manifest instead records OCR-derived, nonempty opposition text fetched October 2, after this forecast. That later availability is not grounds to penalize the candidate for failing to read it. The candidate's original snapshot is not staged, and the evaluator's decided snapshot is not used to reconstruct its information set.
