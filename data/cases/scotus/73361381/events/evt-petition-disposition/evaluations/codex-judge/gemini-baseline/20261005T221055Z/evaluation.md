# Evaluation: gemini-baseline

## Outcome and scores

The cert-stage outcome records denial on October 5, 2026, with actual_granted = 0. The predicted label, denied, matches exactly: correct = 1. The 0.005 grant probability yields Brier = (0.005 - 0)^2 = 0.000025. This scores the disposition, not the predicted conference timing or the Court's reasons.

## Baseline

Use the prediction's frozen baseline band, sal-v4, and docket Term 2025, not the evaluator's terminal context or the resolution's calendar year. The committed metrics/statpack.md heading matches sal-v4. The bracketed reached rates and weighted resolved denominators for every displayed prior Term are: 2024 5.7%/1271; 2023 5.9%/1312; 2022 5.8%/1192; 2021 5.6%/1500; 2020 4.5%/1739; 2019 4.6%/1399; 2018 4.6%/1524; 2017 4.7%/1643. Exclude 2025 and 2026.

The executed resolved-weighted calculation gives 592.925 / 11580 = 0.05120250431778929, an approximate denial-reweighted risk-set rate reconstructed from rounded printed percentages, not an exact grant count. The table renders 10 of 10 Terms, so there is no hidden-window divergence to flag. Skill = 1 - 0.000025 / baseline^2 = 0.9904641896985705. These are committed-pack figures, not a claim about current remote corpus freshness.

## Reasoning quality: 0.60

The rationale identifies the appropriate baseline population and gives a directionally sensible low-grant assessment from the narrow dispute and lack of visible affirmative attention. It makes its downward adjustment explicit. However, the supporting analysis is thin: it largely characterizes the case as state-law-heavy without examining the petition's federal notice-versus-codification theory or its concessions. Missing opposition does not itself establish a response waiver; the rationale labels that inference only as apparent but still relies on it. Pro se status supplies no quantified discount here, and the roughly tenfold reduction from the prior is not developed beyond general heuristics.

The denial supports the outcome call but supplies no merits rationale confirming these explanations. This grade concerns reasoning.md only. The forecast document was read for context; its timing, predicted procedural events, and structured claims receive no discretionary score here.

## Integrity and scope

The retrieval log records forward mode and September 17 calls before resolution. Its queries show local inputs and statistical context, not an attempt to retrieve this petition's result. All results are unobserved; that limits verification and is not evidence of failed or empty retrieval. Neither rationale nor forecast discloses an already-resolved petition. Accordingly, retrieved_outcome_material = false, influenced_prediction = not_applicable, and leakage_suspected = false on the available evidence.

No cert vote accuracy, semantic grades, or harness-owned claim scores are written. The optional independent big-case assessment is omitted because the candidate's stakes score was visible before an independent assessment was formed. No blocking or data-quality anomaly requires flags.json.
