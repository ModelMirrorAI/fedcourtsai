# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage event. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. codex-baseline forecast `denied`, so exact-label correctness is 1. Its probability of any grant was 0.003, producing Brier loss `(0.003 - 0)^2 = 0.000009`.

The baseline uses the prediction's frozen Term 2025, band `baseline`, and `sal-v4`, not the evaluator's decided-docket context. The committed statpack's salience heading matches that version. Pooling its bracketed reached rates over every displayed strictly prior Term, 2017–2024, gives weighted denominator 11,580 and rate 0.05120250431778929. The rate/count pairs in descending Term order are (5.7%, 1271), (5.9%, 1312), (5.8%, 1192), (5.6%, 1500), (4.5%, 1739), (4.6%, 1399), (4.6%, 1524), and (4.7%, 1643). These are denial-reweighted live/historical-slice estimates; the published percentages are rounded, so the pooled rate and derived skill are approximate. The caption displays 10 of 10 Terms, so there is no rendered-window truncation to flag. Terms 2025 and 2026 are excluded. With `base_rate_basis = risk_set`, baseline loss is approximately 0.002621696448413231 and skill is 0.9965671082914854. This is one-event arithmetic, not evidence of population calibration or general forecasting skill. No fresh corpus query or current corpus-status claim is made.

## Reasoning quality: 0.92

The rationale distinguishes the petitioner's advocacy from established facts, identifies the fact-specific evidence and municipal flooding dispute, and explains why generalized uniformity assertions do not themselves demonstrate a review-worthy conflict. It properly treats absent opposition and lower-court materials as limitations rather than proof of waiver, concession, or a dispositive state-law ground. Its discussion of the petition's reported record-citation deficiency is supported by the provisioned petition's page 15, without purporting to establish the appellate court's exact holding. It pools the appropriate prior-Term risk-set anchor and labels its large downward adjustment as judgmental rather than empirically fitted.

The remaining weakness is precision: neither the aggregate band rate nor a comparison cohort establishes a 0.3% case-specific frequency. Missing lower-court and opposition materials also limit the vehicle assessment. The recorded denial is consistent with the forecast but supplies no substantive explanation proving the candidate's proposed reasons. The grade reflects the soundness and uncertainty discipline of `reasoning.md`, not merely a correct denial call.

## Leakage and scoring boundaries

The harness log records forward mode and approximately 92.6% result-capture coverage. September 16 calls precede the recorded October 5 resolution. The case reads concern provisioned materials; outside attempts concern general Court rules. The two unobserved web rows are judged by those queries, not credited as having returned nothing merely because the candidate reported unsuccessful retrieval. No logged query, dated result, or reasoning shows this petition's outcome surfacing early. A file-discovery command excluded the forbidden labeling directory; that exclusion is not a read of its contents. The forward assessment is `not_applicable`, with no suspected leakage.

The prediction's September 16 snapshot is not staged for this evaluator; the later evaluator snapshot is not used to reconstruct its contents. The staged forecast document was read for context only. Neither it nor the quantitative claims contributes to reasoning quality; claim scores remain the harness's. Cert votes are not scored, and this cert event receives no semantic grades. The optional independent stakes assessment is omitted.
