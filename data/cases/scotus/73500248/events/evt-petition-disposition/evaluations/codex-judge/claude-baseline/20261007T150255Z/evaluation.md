# Evaluation: claude-baseline

## Outcome and quantitative scores

This is a **cert-stage** cell. The provisioned outcome records `denied` on **October 5, 2026**, and `actual_granted = 0`. The candidate predicted denial at **P(any grant) = 0.02**. Exact-label correctness is **1** and **Brier = (0.02 - 0)^2 = 0.0004**. The record establishes denial, not judicial endorsement of the lower court's statutory reasoning.

The prediction freezes **baseline**, **sal-v4**, and **Term 2025**. The matching statpack table supplies the bracketed reached rates for the **risk-set** basis. The included rows are 2017 **4.7%, n=1,643**; 2018 **4.6%, n=1,524**; 2019 **4.6%, n=1,399**; 2020 **4.5%, n=1,739**; 2021 **5.6%, n=1,500**; 2022 **5.8%, n=1,192**; 2023 **5.9%, n=1,312**; 2024 **5.7%, n=1,271**. Pooling the displayed rates yields **592.925 / 11,580 = 0.05120250431778929**. The numerator reflects rounded displayed percentages, not an observed integer grant count. The rate describes the pack's denial-reweighted paid-segment live/historical slice.

Neither this case's own Term nor Term 2026 enters the pool. The table shows ten of ten pack Terms, so there is no rendered-window truncation, and its salience version matches the prediction. The baseline is not re-derived from the decided docket. **Brier skill = 1 - 0.0004 / 0.05120250431778929^2 = 0.8474270351771281**. This resolved-event comparison is not evidence of performance over a cohort.

## Reasoning quality: 0.87

The rationale substantially supports its low-probability forecast. It identifies the broad circuit agreement on the question presented and separates that agreement from disagreements over downstream exceptions. The provisioned petition's Appendix A, pages 4a–5a, confirms the panel's reliance on binding precedent and its description of circuit consensus. The candidate correctly recognizes a clean vehicle and a textual counterargument as reasons not to reduce the grant probability to zero. It differentiates the terminal relist table from the petition's current distribution state and anchors on the prior-Term reached population.

The Murphy discussion acknowledges that the prior case did not decide this precise cap question, rather than claiming a direct holding forecloses review. The candidate also discloses limitations in its prior searches and its lack of an opposing Supreme Court brief. These are useful boundaries on the analysis; the evaluator has not fetched Murphy or reconstructed the candidate's search results anew.

The weaker parts are the added inferences about counsel pedigree and the size of the individual verdict, neither supported by a conditional estimate linking those facts to grant probability. The assertion that a future response request would roughly triple the forecast is similarly uncalibrated. The waiver/no-response posture is a sensible downward signal, but the argument sometimes gives it more nearly deterministic force than the available record warrants. These reservations explain the gap from a top reasoning score, despite the strong central vehicle analysis and correct label.

Only the rationale is graded. The forecast document's exact October 5 timing receives no bonus, and the success of its auxiliary claims is not folded into reasoning quality. Mechanical claim probabilities and outcomes are left to the harness.

## Leakage and scope

The log records **forward** mode and **31/31 captured calls**. All calls occurred on September 17, before the October 5 denial. Queries include the case caption, this docket's entries, broader corpus priors, and the Murphy opinion. The explicit retrieved-document date is **February 21, 2018**. Forward retrieval of an open case's docket is permitted; an after-baseline inquiry would not itself be a replay-boundary violation.

The retrieval note says the docket query returned no entries and no disposition surfaced. Captured digests are evidence of capture, not the full result text; I do not independently assert their contents from the digests alone. A separate logged command inspected prediction artifacts outside this docket. That command is not evidence that this event's disposition was retrieved; I did not follow its paths or infer a candidate identity. The rationale contains no premise that presupposes the Supreme Court denial. Predicting the first post-conference order date correctly is not, by itself, evidence of leakage.

On the available log, timing, and prose, `retrieved_outcome_material = false`, influence is `not_applicable`, and `leakage_suspected = false`. The evaluator's October 5 snapshot is not treated as evidence of what the September 17 prediction saw.

No cert-vote accuracy or semantic grading is supplied. Harness-owned claim scores and provenance remain absent. The baseline uses the committed pack only; no live corpus query or remote-freshness representation is made.
