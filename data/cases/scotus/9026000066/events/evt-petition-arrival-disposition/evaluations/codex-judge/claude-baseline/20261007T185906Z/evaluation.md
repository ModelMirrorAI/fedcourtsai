# Evaluation: claude-baseline

## Outcome and score

The supplied cert outcome is `denied`, resolved October 5, 2026, with `actual_granted = 0`. The prediction matches that label: correctness **1**. Brier loss is `(0.005 - 0)^2 = 0.000025`. This is one correct low-probability forecast, not a calibration finding.

## Analysis quality: 0.80

The rationale clearly separates its arrival-population anchor from case-specific adjustments. It supports the downward judgment with the petitioner's pro se status, the state dissolution posture, the memorandum disposition, no developed inter-court conflict, and missing-record vehicle problems. The provisioned petition supports that factual account. It also candidly states that the corpus query returned nonanalogous denials and did not inform its probability.

The main weakness is numerical overstatement: calling the terminal-band rate an upper bound on this petition's chance is not justified merely by a population average. Several frequency assertions about representation and family-law petitions are stronger than the evidence shown, and the adjustment to 0.5% remains judgmental rather than estimated from comparable cases. The discussion identifies the petition's reviewability authorities but gives limited attention to the alleged exception to the state procedural barrier. A correct denial does not establish that any of those barriers supplied the Court's actual reason.

## Baseline and scoring boundaries

The frozen context is `baseline`, `sal-v3`, Term 2026; the committed statpack now labels its segment table `sal-v4`. Accordingly, no segment rate or skill score is written, and the basis is null. The shared flags record this mismatch. I neither substitute a terminal rate nor judge the historical anchor incorrect merely because today's table uses a different version.

Quality is assessed only on the rationale's analysis of its headline estimate. The forecast document and structured claim probabilities are not scored here, including the claim discussion embedded in the rationale. Claim scores remain the harness's responsibility. Cert-stage votes and semantic grades are not scored.

## Leakage

The captured log records forward mode with result-capture coverage 1.0. Calls and prediction occurred August 16, before the October 5 denial. The generic corpus-priors query carries an August 9 document date; it does not seek this petition's outcome. No query or prose presents the eventual denial as already known. Influence is `not_applicable`, and no leakage exclusion is warranted. Capture coverage is not a claim that every underlying result body is reproduced in the staged log.
