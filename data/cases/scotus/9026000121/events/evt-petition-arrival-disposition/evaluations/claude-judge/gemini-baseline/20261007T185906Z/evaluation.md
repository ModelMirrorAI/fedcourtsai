# Evaluation — gemini-baseline — scotus/9026000121 — evt-petition-arrival-disposition

**Stage:** cert (petition, arrival moment). **Outcome:** denied on 2026-10-05 after respondents waived and the petition was distributed once for the 2026-09-28 conference; no noted dissent. `actual_granted = 0`.

## Quantitative

- `correct = 1` — `predicted_disposition: denied` matches `actual_disposition: denied`.
- `brier_score = 0.000001` — `(0.001 − 0)²`.
- `segment_base_rate`, `brier_skill_score`: **omitted**, `base_rate_basis` null. The prediction froze `context.band = baseline` under `context.salience_version = sal-v3`; the committed `metrics/statpack.md` band table is headed **sal-v4**. The table is therefore no baseline for this band, and the contract's only answer is to omit rate and skill together and flag the mismatch (`flags.json`). I did not relabel to `terminal`.
- `vote_accuracy`: omitted (cert cell).
- `judgment_correct`: null.
- `claim_scores`: not mine; left absent for the harness.

## Reasoning quality: 0.50

The rationale is right in direction and reaches the right anchor (a baseline-band bracketed `reached` rate of "roughly 5-7%"), and its stated reasons for cutting are real: no split, fact-bound and poorly drafted questions, state-law error correction, no federal interest. The conditional summary-route reasoning (the petition itself asks for summary reversal) is a fair point.

What keeps the score at the midpoint:

- **The number is not argued.** 0.001 is a fifty-to-seventy-fold cut from the stated anchor and sits below the terminal floor of the weakest band in any Term (0.6%–1.8% on the rendered table). Nothing in the paragraph explains why this petition is an order of magnitude less likely than the typical baseline-band denial. "Highly idiosyncratic" is a label, not a reason. The outcome rewarded the number, but the rationale would read the same way on a petition that was granted, which is the test for whether the analysis did the work.
- **It does not engage the record's specifics.** The other two rationales located the petition's actual weaknesses: the Appellate Court of Maryland's finding that the LinkedIn evidence did not show the judge was practicing law when he signed the order, the petition's own concession on the timing, the unreported decision below, the Supreme Court of Maryland's procedural dismissal and the adequate-and-independent-state-ground problem it creates. This rationale mentions none of them and reads as if written from the questions presented alone (which the log's query profile is consistent with: the petition body itself was not read).
- **No uncertainty is stated.** The absence of a brief in opposition at arrival, the unseen state high-court decision, the approximate pooled anchor: none is acknowledged.

One descriptive note, kept out of the score because the claims block is scored in code and not by me: the rationale reads `relist-increment` as "a relist" and sets 0.02, whereas the declared claim at a zero-distribution arrival is whether the petition is distributed at least once more, which nearly every paid petition is (and this one was). That is a claim-semantics misread rather than a legal-analysis error, and the harness scores it where it belongs.

Scored on `reasoning.md` only. The forecast document was read for context and is not scored.

## Leakage

`mode = forward`, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. The log (25 calls) is wholly `unobserved` (`result_capture_coverage = 0.0`), which is the engine's standing capture shape rather than a defect, so each call is graded on its query: reads of the prompt, AGENTS.md, the schema, the provisioned snapshot, context and documents, and a grep of the statpack band table. No web search, no CourtListener call, no corpus query, no read under `data/qp-topics/`. The prediction (2026-08-16) predates the distribution and the denial, and the rationale cites nothing later than the arrival-time docket. No sign of a decided case provisioned forward. Because every result is unobserved I cannot say what any read returned, only what it asked for; none asked for anything outside the provisioned inputs.

## Big-case read

`evaluator_score = 0.05`. A private Maryland fee dispute with a novel but factually unproven judicial-eligibility due-process angle; no split, unreported decision below, procedural dismissal by the state high court, waiver, one distribution, silent denial, no amici. Formed from the docket, the petition, and the outcome. The staged `prediction.json` places the predictor's own `big_case_score` in view when the file is read; my read rests on the record, not on that number.
