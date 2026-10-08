# Evaluation: codex-baseline

## Outcome and quantitative score

The cert-stage outcome is `denied`, resolved October 5, 2026, with `actual_granted = 0`. The candidate's disposition is an exact match: **correct = 1**. Its 0.004 grant-family probability gives **Brier = (0.004 - 0)^2 = 0.000016**. The outcome supports the denial call but supplies no explanation adopting the candidate's legal analysis.

Cert votes are not scored. The forecast document and quantitative claims were read but are not graded here or folded into reasoning quality. The harness computes claim scores; no semantic set is declared on this cert event.

## Reasoning quality: 0.90

The rationale is specific and well tied to the supplied petition. It separates the asserted general duty to explain disqualification rulings from the petition's reliance on exceptional-bias precedents, notes the lack of concrete bias facts or identified conflicting decisions, and treats the pending enforcement action and extraordinary-writ posture as vehicle concerns rather than conclusively resolving jurisdiction. It acknowledges the absence of a provisioned opposing brief at prediction time and avoids converting uncertain filing chronology into a definitive timeliness defect. Those qualifications matter more than the fact that denial ultimately occurred.

The candidate also distinguishes a frozen arrival risk-set anchor from a terminal trajectory rate and labels its small originating-court comparison as secondary. Its cited historical counts are not independently verified against the differently versioned current table. The main remaining weakness is calibration: the precise reduction from approximately 6.56% to 0.4% is judgmental, not established by a demonstrated matched comparison group. The analysis is therefore strong but not conclusive. No credit or penalty is assigned for the outcomes of individual structured claims or the separate forecast prose.

## Baseline version mismatch

The frozen band is `baseline` under `sal-v3`, with Term 2026. The committed statpack's salience-band table is `sal-v4`, so its rates cannot be paired with this frozen band. `segment_base_rate` and `brier_skill_score` are omitted, and `base_rate_basis` is null. I neither reuse the candidate's own historical rate as an evaluator baseline nor relabel the current table's rate as terminal. The cell-level flag records this mismatch. It is not a predictor reasoning defect.

## Leakage assessment

Context and log both record forward mode. The August 16 prediction precedes the October 5 disposition. The listed calls show record and statistical-context inspection, not retrieval of the later cert denial; result-capture coverage is 1.0 for those calls. Capture coverage describes the listed calls, not a guarantee of complete activity coverage. In particular, the retrieval note reports a general due-process authority search stopped by a rate limit and a Caperton citation lookup yielding no rows, but these operations are not individually identifiable in the staged log. I treat those reported failures as self-report, not independently observed results. Their stated subjects do not seek this case's eventual outcome.

The rationale explicitly declines to use later-than-arrival stay activity and discusses date inconsistencies without presupposing denial. Such activity would in any event be permissible forward signal while the petition remained unresolved. Nothing visible establishes that an already-decided cert case was provisioned forward. `retrieved_outcome_material` is false, influence is `not_applicable`, and `leakage_suspected` is false.
