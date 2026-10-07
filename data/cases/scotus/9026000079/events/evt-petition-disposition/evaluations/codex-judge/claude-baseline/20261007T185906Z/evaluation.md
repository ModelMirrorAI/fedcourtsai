# Evaluation of claude-baseline

## Outcome and scores

This is a cert-stage event, resolved by denial on October 5, 2026, with `actual_granted = 0`. claude-baseline predicted `denied` at P(any grant) = 0.02. Correctness is 1 and Brier loss is `(0.02 - 0)^2 = 0.0004`.

## Baseline

The scored prediction freezes Term 2026, band `baseline`, and salience version `sal-v4`; the committed table uses that same version. The appropriate basis is `risk_set`, using bracketed `reached` figures over all displayed Terms before 2026. In descending order, the 2025–2017 rate/weighted-denominator pairs are 3.9%/1140, 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643.

Pooling gives 637.385/12,720 = 0.05010888364779874. This numerator is reconstructed from rounded percentages, not an observed integer grant count. The baseline is a denial-reweighted paid-segment estimate from the committed artifact, not a current corpus query. No corpus-refresh timestamp is supplied in the consulted markdown. All 10 of the pack's 10 Terms are rendered, and the case's own 2026 row is excluded, so there is no rendered-window discrepancy. Skill is `1 - 0.0004 / baseline^2 = 0.8406945856527439`. The evaluator's terminal context does not determine the band.

## Reasoning quality: 0.86

The rationale connects the response waiver to the petition's procedural posture and goes beyond the docket skeleton by identifying a specific lower-court memorandum. As described in the rationale, the timeliness ruling, unpreserved tolling and retroactivity arguments, and alternative merits disposition create multiple vehicle obstacles. That is a materially more discriminating account than merely inferring weakness from low overall cert rates. The analysis also distinguishes the risk-set anchor from terminal zero-relist statistics and treats a possible later hold/GVR as a reason not to set grant probability to zero.

The evidence trail supports that the candidate sought and extracted the January 15 memorandum; the blinded log does not reproduce its complete text, so this evaluation does not independently certify every doctrinal characterization. The petition itself remained unavailable. The claim that resolving timeliness would necessarily change nothing is stronger than can be established from this limited record, and the proposed future better-vehicle/GVR route identifies no concrete pending lead case. The numerical adjustments remain judgmental. These qualifications limit the grade despite substantial case-specific analysis. The denial is consistent with the forecast but supplies no explanation confirming the candidate's account of the Court's motivation.

I grade only the analytical rationale in `reasoning.md`. I do not grade the forecast document, compare its predicted questions or writings with the outcome, or assign scores to the claims block. No cert votes or semantic propositions are scored.

## Leakage

The mode is forward. All 38 logged calls have captured results and occurred October 4, before the October 5 resolution. The live docket lookup expressly sought any disposition, but such a query is permissible for a genuinely pending forward event. The candidate reports a docket ending at the distribution entry and reasons about the coming order list, not a known denial. The January 15 lower-court decision and background precedent predate this event's resolution and are not its outcome. Corpus queries concerned broader context rather than a recorded denial of this petition.

Capture coverage of 1.0 means the harness observed results, not that every result body or document date is reproduced in the staged log. I do not treat null dates as proof of clean retrieval. Considering call timing, query scope, and the explicit pending-case account together, no outcome-revealing material or forward mis-provisioning is evidenced. I record retrieval false, influence `not_applicable`, and suspicion false.
