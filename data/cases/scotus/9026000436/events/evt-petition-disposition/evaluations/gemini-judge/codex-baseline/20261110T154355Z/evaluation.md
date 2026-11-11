# Evaluation of `codex-baseline`

## Overview and quantitative summary

This is a **cert-stage** evaluation for *Radiall USA, Inc. v. Gary T. Ramadei* (`scotus/9026000436`, event `evt-petition-disposition`). The petition was distributed once on October 7, 2026 for the November 6, 2026 conference and was denied on November 9, 2026 (`actual_disposition = "denied"`, `actual_granted = 0`, `signals.distribution_count = 1`, `signals.cvsg_date = null`, `noted_dissent_from_denial = false`).

`codex-baseline` predicted `denied` with `probability = 0.07`, yielding `correct = 1` and `brier_score = 0.0049`. Because `0.07` is above the stamped segment base rate, its Brier score is slightly worse than a naive baseline forecast.

## Assessment of `reasoning.md` (`reasoning_quality = 0.91`)

### Strengths
- **Precise empirical anchoring:** Checked against the statpack build in force at prediction time (`statpack-at` build `0918fb18e74f` / alternative `1c4f550b7b75`, `sal-v4`, as distinct from the currently committed `sal-v8` statpack), `codex-baseline` computed the exact prior-Term (`2017–2025`) pooled risk-set rate for `baseline` from `statpack.json`, matching build `0918fb18e74f`, and clearly distinguished risk-set rates from terminal relist/CVSG buckets.
- **Detailed, accurate analysis of Appendix A:** `codex-baseline` closely read the Second Circuit's March 19, 2026 summary order (Appendix A, pages 2a–5a) and identified the multiple independent preservation barriers that defeated petitioner's futility narrative: (1) Radiall's affirmative invitation of the motivating-factor jury instruction; (2) Radiall's failure to challenge *Woods* under *Gross*, *Nassar*, and *Comcast* (all of which predated the litigation) or to raise *Loper Bright* in its October 2024 post-trial motions (filed more than three months after *Loper Bright*); and (3) the absence of plain error on an unsettled question. It also astutely noted that extending *Dupree* from a legal issue preserved at summary judgment to an unraised and invited instruction required an additional contested step.
- **Verification of *Loper Bright*'s statutory stare decisis holding:** Using CourtListener MCP, `codex-baseline` checked *Loper Bright*, 603 U.S. at 412–413, confirming that the Court preserved statutory stare decisis for prior holdings that relied on *Chevron*, which undercuts any routine remand or automatic-overruling theory.

### Minor weakness
- **Modest upward adjustment over baseline:** Given the compounding preservation obstacles (`invited error` + post-*Loper Bright* October 2024 post-trial forfeiture + non-precedential summary order) that `codex-baseline` itself laid out persuasively, adjusting *upward* from the baseline risk-set rate to `0.07` (and `0.25` conditional summary disposition route) was slightly generous, though its secondary increment probabilities (`relist-increment = 0.20`, `cvsg-increment = 0.02`, `dissent-from-denial = 0.04`) were well-proportioned.

## Predicted reasoning (`predicted_reasoning_quality = 0.90`)

In `predicted_reasoning.md`, `codex-baseline` committed to four central claims:
1. **Denial on an orders list shortly after the November 6, 2026 conference (in November 2026) with zero additional distributions (`P = 0.20`)** (`borne-out`): The petition was denied on November 9, 2026 with `distribution_count = 1`.
2. **No CVSG (`P = 0.02`)** (`borne-out`): No CVSG was issued (`cvsg_date = null`).
3. **Conditional on a grant, plenary review (75%) on Question 1 alongside the threshold preservation issue rather than summary disposition (25%)** (`unresolved`): Untested because certiorari was denied.
4. **Ordinary denial with no noted dissent or statement respecting denial (`P = 0.04`)** (`borne-out`): The November 9, 2026 denial was issued without any separate writing.

`codex-baseline`'s forecast document was specific, well-reasoned, and decisive on every realized dimension (timing, zero additional distributions, no CVSG, and no separate writing).

## Leakage assessment

`codex-baseline` ran in `forward` mode on October 9, 2026, a month before the November 9, 2026 denial. Its retrieval log (33 calls, `result_capture_coverage = 0.939`) shows local file reads (including a safe `find data -name AGENTS.md -not -path 'data/qp-topics/*'` that opened no files under `data/qp-topics/`), two unobserved web-search calls targeting the 2024 *Loper Bright* opinion PDF, and CourtListener MCP searches of *Loper Bright* (`603 U.S. 369`), with no queries targeting this petition (`retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`).
