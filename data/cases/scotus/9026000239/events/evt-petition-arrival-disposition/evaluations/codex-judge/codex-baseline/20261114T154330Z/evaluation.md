# Evaluation: codex-baseline

## Outcome and accuracy

This cert-stage arrival event resolved on November 13, 2026. The docket grants review limited to Questions 1 and 2, and outcome.json labels the result `granted` with a `plenary` route. Exact comparison with the candidate's `granted` label yields **correct = 1**. The probability 0.92 gives **Brier = (0.92 - 1)^2 = 0.0064**.

Cert-stage votes are not scored. There is no merits judgment comparison or semantic-grade block. Structured quantitative claims and the stamped segment base rate, basis, and skill score are reserved to the harness.

## Reasoning quality: 0.90

The rationale correctly starts with the frozen federal-band arrival population and pools only prior Terms, explicitly rejecting the terminal relist-zero population. It supports an upward departure with the government's role, the divided appellate decision, national policy stakes, and substantial remedial questions. It also distinguishes an asserted analogy to Al Otro Lado from a holding directly controlling asylum eligibility for people already physically present in the country.

Especially useful is its engagement with the opposite statutory case: the text of Section 1158(a)(1), the lower court's treatment of removal procedures, the absence of an inter-circuit conflict, and the possibility of narrower grounds. The document acknowledges the lack of an opposition brief and the incomplete appendix rather than pretending to possess a balanced full record. These features make the analysis stronger than a bare importance-based prediction even though the numerical uplift remains judgmental. The mandate stay was unopposed, so it is not an independent endorsement of certworthiness; the rationale could qualify that signal and better explain why the counterarguments leave the final number so high. I grade the quality of this rationale alone, not its claims block or separate forecast.

The candidate-era statpack was reconstructed with `statpack-at`: build `02dd6a20fccc232651e3e13cdea3da3066e41c5b`, digest `sha256:5b70d73d2cadac0dff2091d5aa32536fb116a3366f76592493006ca63337d0cc`. This is the run-inferred historical build, with no candidate-pinned digest and no alternative build reported. Its sal-v3 table supports the cited pooling population and method; I do not replace the stamped segment base rate with a separately quoted pooled figure. The staged petition also cites Al Otro Lado and presents the legal distinction; I have not independently fetched that authority's opinion.

## Predicted reasoning

**Grade: 0.84.** The document correctly forecasts a prompt grant after the initial conference or one relist, no CVSG, and a plenary rather than summary route. The two recorded conferences culminated in the November 13 grant. It also predicts a hierarchy among the questions: Question 1 first, Question 2 potentially included, and Question 3 less likely to receive independent review. The order takes exactly Questions 1 and 2. That provides discriminating content beyond a generic grant call, but the inclusion of Question 2 and exclusion of Question 3 were hedged, so the exact limited grant earns less credit than a definite forecast of that scope would.

The conditional merits reversal remains unresolved. The cert order establishes neither the eventual merits ground nor the merits lineup. A hypothetical silent denial was never tested. These unresolved branches are not counted as misses, and this forecast grade does not alter reasoning_quality or the mechanical claim scores.

## Leakage

The harness records **forward** mode and August 24 calls, preceding the November 13 grant. Overall capture coverage is approximately **0.912**, but the three direct CourtListener rows are **unobserved**: their null dates do not prove empty or safe returns. Their queries concern a cited related authority and its opinion, and the rationale places that decision on June 25, before the arrival forecast. An earlier related ruling is permissible forward information, not this petition's own outcome. Nothing in the available queries or reasoning shows the November grant, its question limitation, or later docket signals. Accordingly retrieved_outcome_material is false on the available evidence, influence is not_applicable, and leakage_suspected is false. The observation limitation is stated without treating normal capture differences as a defect.

## Significance

Independent stakes assessment: **0.94**, based on the nationwide immigration/asylum policy and remedial questions, not the candidate's salience score.
