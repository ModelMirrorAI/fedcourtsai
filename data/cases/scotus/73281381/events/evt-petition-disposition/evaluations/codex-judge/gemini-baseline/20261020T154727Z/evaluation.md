# Evaluation: gemini-baseline

## Outcome and scores

This is a cert-stage petition-disposition cell. The committed outcome records denial on October 19, 2026, with `actual_granted = 0`. The candidate called `denied`, so correctness is 1. Its grant probability was 0.22: Brier = (0.22 - 0)^2 = 0.0484. Denial does not establish that the lower court's constitutional analysis was correct or disclose why the Court declined review.

The scored prediction froze the elevated band under sal-v4. Baseline, basis and skill are left to the harness; the terminal high band in this evaluator's context does not replace the prediction's frozen band. No vote accuracy or semantic grades are appropriate on a cert cell. Quantitative claims and the forecast document are not scored here.

## Rationale quality: 0.62

The rationale identifies a meaningful distinction between tax-related surplus retention and police-power forfeiture, recognizes the absence of an articulated circuit split, and treats a requested response as affirmative attention rather than a guarantee of review. Keeping denial the modal disposition is coherent with those considerations.

The central weakness is calling the issue cleanly presented without confronting the principal vehicle objection. The provisioned opposition's pages 11-15 emphasize the exclusively facial challenge, valid applications involving no surplus, and the difference between a facial claim and particular confiscations; the petition itself acknowledges the facial ruling below. These are material obstacles to obtaining review of the broad question, not peripheral merits details. The upward adjustment for the issue's importance consequently receives less support than the rationale suggests. The approximate base-rate reference also leaves its pooling window and arithmetic insufficiently explicit. The quality grade concerns this analysis, not whether the separate forecast or claims happened to resolve correctly.

## Leakage and stakes

The harness log records forward mode. Its 35 calls have 0% result-capture coverage; I do not interpret their null dates as proof that searches returned nothing. The logged queries and prose reveal no October 19 disposition or other evidence that this petition had already been decided when predicted on September 16. The assessment is `not_applicable`, with no suspected leakage, subject to that visibility limitation.

My stakes assessment is 0.60: limits on municipal vehicle confiscation have potentially broad constitutional and practical importance, but this facial, ordinance-specific vehicle constrains reach. This is not a probability of review or an agreement score.
