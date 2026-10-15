# Evaluation: codex-baseline

## Outcome and mechanical scores

This is an **interim** application, not a certiorari or merits event. The prediction assigned 0.82 to an unqualified grant and selected `granted`. The authoritative outcome records `denied`, `actual_granted: 0`, resolved October 14, 2026. The provisioned October 14 docket specifies denial **as moot**. Therefore `correct = 0` and `brier_score = (0.82 - 0)^2 = 0.6724`.

Mootness is important to interpretation: this disposition does not establish that the Court rejected the applicant's underlying jurisdictional theory, endorsed the mandamus reasoning, or balanced the equities against applicants. The outcome supplies no reasoning for deciding those substantive questions. No such holding is inferred here.

## Reasoning quality: 0.80

The rationale accurately separates substantive relief from an administrative pause and identifies the relevant stay requirements. It grounds the upward adjustment in the earlier September stay, the compressed agency timetable, and the competing appended opinions. Most importantly, it fairly explains the distinction between compelling the Commission to decide and dictating its decision. Its account of Wynn's concurrence is supported by the provisioned application, App. 35–37. It recognizes that requiring agency action may satisfy, rather than evade, the prerequisite to judicial review, and that harm from a compelled decision is not identical to harm from changing advertising rates.

The rationale also acknowledges the missing opposition, the already-passed October 9 deadline, possible agency action, and procedural termination. Those qualifications show that the ultimately important procedural risk was available to the analysis. The principal weakness is the jump to an 82% unqualified-grant probability despite that unresolved timetable and those substantial counterarguments. The prior stay is a meaningful signal but does not itself establish entitlement to a stay of a distinct mandamus order or rule out mootness. The numerical adjustment remains judgmental rather than supported by a conditioned historical model. This limits the quality score without treating an incorrect forecast as automatically unsound legal analysis.

The quality grade assesses `reasoning.md` only. The forecast document was read for context, not graded; neither its procedural predictions nor the quantitative claims enter this grade.

## Baseline and scope

The rationale uses strictly prior application-Term counts and describes parsing and selection limitations rather than substituting a cert salience band. The committed statpack's interim section supports the stated pooling method and clears the published pooled-sample floor. I do not emit a separately calculated baseline or skill figure: both are harness-owned on interim cells, and comparison is to the stamped segment base rate. `base_rate_basis` remains null. No corpus query was made, and the committed pack is not represented as a fresh corpus measurement.

No vote accuracy or semantic grades are written on this interim event. Quantitative claim scores, context, and process provenance remain the harness's responsibility.

## Leakage and conditioning

The candidate's own frozen context and captured log both say `forward`. Its October 9 cutoff bounded the snapshot, not forward retrieval. The September 4 stay predates the resolution of this application and is legitimate background. Nothing in the available log or rationale shows this application's October 14 denial being retrieved or presupposed. The forward default therefore applies: no suspected outcome influence.

There is a material audit limitation: the staged log has only four statpack-related calls, although `retrieval.md` describes additional authority searches and local reads. Its 1.0 capture fraction is not proof that all activity was logged. This discrepancy is flagged without converting incomplete telemetry into affirmative leakage evidence. The prediction timestamp and resolution fall on the same date; their intraday ordering cannot be established from the provisioned resolution date alone.

The event says `response-requested`, while the prediction froze `response_requested: false` and reports a one-entry snapshot. The candidate explicitly identifies that mismatch rather than silently treating the rung as observed. The evaluator's later docket contains the October 8 response request, but that later snapshot cannot establish what the predictor was given. A shared conditioning flag records the discrepancy; it is not itself outcome leakage.
