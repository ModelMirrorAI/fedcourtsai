# Evaluation: gemini-baseline

## Cell

Cert stage, arrival moment (`evt-petition-arrival-disposition`). Outcome: `denied` on 2026-10-13 after one distribution, `actual_granted` 0, no noted dissent from denial. The prediction froze `context.band` = `baseline` under `sal-v4`, so the segment base rate, the Brier skill score and the basis are stamped by the harness. I left all three null and quote no rate of my own here: the comparison is against the stamped segment base rate. `claim_scores` is the harness's and I did not grade the forecast document or the claims. No semantic set is declared for a cert cell, so there is no `semantic_grades` block. `vote_accuracy` is omitted because this is not a merits cell.

## Scores

- Predicted `denied` at P(grant) = 0.015. `correct` = 1. Brier = 0.015² = 0.000225.

## Reasoning quality: 0.55

The rationale is one paragraph. Its essentials are right: a baseline-band anchor of about 5% over 2017–2025, a downward adjustment because the petition alleges no split, and a characterization of the case as error correction of a circuit's state-law reading, a poor cert vehicle. Those are the factors that drove the denial. But it shows little work. It does not say which statpack rate it pooled (reached or terminal) or how. It does not engage the panel opinion's actual grounds or the certification alternative. Its claim that the case is "highly technical" stands in for analysis of why the Erie framing fails. The conclusion is well calibrated but thinly supported, so a reader cannot audit the adjustment from 5% to 1.5%.

## Leakage

Forward cell. The prediction was made 2026-09-27, before the 2026-10-13 resolution. The log shows only local reads of the provisioned record, the prompt and the statpack (results unobserved, graded on the commands). There was no web or MCP retrieval. Graded `not_applicable`, not suspected.
