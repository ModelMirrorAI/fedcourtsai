# Evaluation: codex-baseline

## Outcome and numerical scores

The event is cert-stage. The supplied outcome records `denied`, `actual_granted = 0`, on October 5, 2026. codex-baseline predicted `denied` on September 16 with grant probability 0.015. Exact-label accuracy is 1; Brier loss is `(0.015 - 0)^2 = 0.000225`. A bare denial does not establish which of the parties' arguments persuaded the Court.

The prediction froze `baseline`, `sal-v4`, and Term 2025. The matching committed statpack table therefore supplies a **risk-set** baseline from its bracketed reached figures, not terminal-band rates and not the evaluator's current context. The pooled rows are:

| Term | Reached rate | Weighted resolved n |
| --- | ---: | ---: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

The executed resolved-weighted calculation gives 0.05120250431778929 over weighted n = 11,580. These are rounded displayed, denial-reweighted estimates for the paid live/historical slice, not exact reconstructed counts or a fresh corpus census. All 10 of 10 pack Terms are displayed; only the eight strictly before 2025 enter, so there is no rendered-window discrepancy. No corpus query or freshness claim is made. Baseline Brier loss is approximately 0.002621696448413231; `1 - 0.000225 / baseline_loss = 0.9141777072871345`. This describes one forecast's loss relative to its permitted baseline, not aggregate skill or calibration.

## Reasoning quality: 0.94

The rationale is grounded in both sides' provisioned advocacy and carefully distinguishes their assertions from established facts. It identifies the strongest negative signal, the analogous January denials, without treating those denials as precedential approval. It also states the best affirmative argument: the distinction between a signed judgment and a later indorsement, Article 66(d)(2)'s post-trial-processing language, and the concurrence's timing concerns. It then addresses the opposition's signing-versus-entry distinction and the concurrence's agreement with the result. These distinctions appear in the opposition at pp. 7–9 and make the downward probability adjustment intelligible rather than outcome-driven.

The analysis correctly keeps the immediate military-review question distinct from the underlying civilian firearms disagreement (petition p. 19 n.6). It preserves the uncertainty about the particular section 922(g) subsection (petition p. 16 n.3), and treats the temporary memorandum as reducing prospective importance rather than extinguishing the alleged continuing injury (petition p. 10 n.2; opposition p. 10). It identifies unverified alternative remedies, the missing reply, and its lack of independent appendix review. The prior-Term risk-set anchor is transparent and avoids terminal-state relist associations as forward conditional probabilities.

The remaining limitation is chiefly quantitative: neither the exact 1.5% probability nor the size of the adjustment is empirically fitted, and the unread reply could distinguish the rejected companion petitions. Those limits are acknowledged rather than concealed. This high score grades the soundness of `reasoning.md`, not length, successful guessing, ancillary probabilities, or the separate court forecast. No cert-stage votes or semantic propositions are scored; the harness owns quantitative claim scores. No independent big-case assessment is supplied.

## Leakage assessment

The log and frozen prediction context both say forward. The 29 logged calls occurred on September 16, 2026, before the outcome's October 5 resolution. Twenty-six have captured results; the three web calls are unobserved, yielding capture coverage 0.896551724137931. Their visible queries concern Goldsmith, Article 66(d)(2), and the official statutory page, not this case's outcome. The candidate's assertion that no useful results returned is not independently established by an unobserved log, and I do not treat null dates or missing digests as empty results.

The local read queries and reasoning identify the pre-decision snapshot, provisioned briefs, and prior-Term statpack. The January companion denials are disclosed as other petitions' preexisting outcomes. Neither the rationale nor forecast presupposes Myslow's denial, and no query targets its later disposition. The evaluator's post-decision record is not used to infer what the predictor was provisioned. On this evidence the forward default applies: `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. Missing result capture for these general-law calls is an audit limitation, not evidence of leakage or a defect requiring a flag.
