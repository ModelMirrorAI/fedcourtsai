# Evaluation: codex-baseline

## Outcome and scores

The cert-stage outcome records denied on October 5, 2026, with actual_granted = 0. The predicted denied label earns correct = 1. P(grant) = 0.008 yields Brier = 0.000064. Neither the denial nor this low loss resolves the merits of the petition's federal theory.

## Baseline

Use the candidate's frozen baseline band under sal-v4 and docket Term 2025. The sal-v4 heading matches. The committed metrics/statpack.md bracketed reached rates and denominators for every displayed strictly prior Term are: 2024 5.7%/1271; 2023 5.9%/1312; 2022 5.8%/1192; 2021 5.6%/1500; 2020 4.5%/1739; 2019 4.6%/1399; 2018 4.6%/1524; 2017 4.7%/1643. Exclude 2025 and 2026, irrespective of the 2026 disposition date.

The executed weighted pool is 592.925 / 11580 = 0.05120250431778929. It approximates the risk-set rate from rounded published percentages and weighted denominators; 592.925 is not an observed integer grant count. The table renders 10 of 10 Terms, so no unavailable-row window discrepancy requires a flag. Skill = 1 - 0.000064 / baseline^2 = 0.9755883256283405. These are figures from the committed pack, without a claim about the remote corpus's present freshness.

## Reasoning quality: 0.92

The rationale clearly identifies the federal notice question and separates the alleged absence of codification from the different question of enactment and publication. It engages with the petition's concessions and the precise transition-language quotation rather than adopting its looser paraphrase. It also recognizes the internal complaint-year discrepancy without inventing a procedural defect. The distinction between a demonstrated conflict on the federal question and conflicting applications of state law is carefully drawn.

The candidate uses the correct frozen-band prior, states the approximation from rounded table entries, and distinguishes statistical background from a fitted case-specific probability. Its account of the retrieved general precedent expressly limits the inference rather than claiming that the earlier opinion decides this petition's precise issue. It acknowledges that preservation, alternative grounds and the asserted conflicting decisions were not independently verified. Missing lower-opinion or opposition material is treated as uncertainty, not proof of waiver or a bar to review.

The remaining limitation is that the reduction from roughly 5.12% to 0.8% is judgmental and not supported by a calibrated comparison set. The incomplete verification of the supposed conflict also leaves residual uncertainty. The high grade is for the soundness and restraint of reasoning.md, not the low numerical loss. No points are assigned for forecast-document details, the claims block, or agreement with the candidate's stakes estimate. The recorded denial supplies no explanation confirming the candidate's proposed doctrinal obstacles.

## Integrity and scope

The log records forward mode, 26 calls on September 17, and capture coverage 25/26. The only unobserved result is a search about Texaco and legislative publication. Despite the retrieval note's description of no usable payload, the log proves only noncapture; I do not treat that result as empty. Its query concerns general older doctrine, not this petition's outcome. Other queries and the rationale contain no already-decided material about this case. Influence is therefore not_applicable, retrieved_outcome_material = false, and leakage_suspected = false.

No cert vote score or semantic block is written; mechanical claim scoring and stamps remain with the harness. The optional independent big-case read is omitted because the candidate's score had already been seen. There is no blocking or data-quality issue requiring flags.json.
