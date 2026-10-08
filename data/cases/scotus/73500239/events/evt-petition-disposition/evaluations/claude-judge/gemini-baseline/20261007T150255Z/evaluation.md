# Evaluation of gemini-baseline — scotus/73500239, evt-petition-disposition

**Cell:** cert stage, forward mode. **Outcome:** petition denied on the October 5, 2026 order list after a single distribution for the September 28, 2026 conference; no CVSG, no relist, no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`, `noted_dissent_from_denial: false`).

## Scores

- **correct = 1.** Predicted `denied`; actual `denied`.
- **brier_score = 0.0001.** P(grant) 0.01 against actual 0.
- **segment_base_rate = 0.0512, base_rate_basis = risk_set.** The prediction's frozen context carries `band: baseline` and `salience_version: sal-v4`, and the committed `metrics/statpack.md` band table is headed `sal-v4`, so the version matches and the risk-set basis applies. I pooled the bracketed `reached` baseline figures, resolved-weighted, over the rendered Terms strictly before the case's Term (OT2025): OT2017–OT2024 (5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, 4.7%/1643), giving 592.9/11580 ≈ 5.12%. The caption says all 10 of the pack's 10 Terms are rendered, so the rendered window is the pack's window and no lookback divergence arises. The rate is approximate to the extent the table's percentages are rounded.
- **brier_skill_score = 0.9619.** 1 − 0.0001 / (0.0512 − 0)².
- **reasoning_quality = 0.5.**
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: not applicable on a cert cell; `claim_scores` is the harness's.

## What the reasoning got right and wrong

The rationale is one paragraph and its structure is sound: it names the right band, identifies the respondents' waiver as the dominant signal, correctly observes that the Court rarely grants without first calling for a response, and reads the third question presented as fact-bound. The resulting 1% was the best-calibrated number of the three on a denial.

What holds the score down is the thinness of the case-specific work. The retrieval log shows the candidate read the questions presented and the docket snapshot but never opened the provisioned `petition.txt`, so its vehicle assessment rests on the QP wording alone. It therefore misses the facts that actually make this a poor vehicle: the Sixth Circuit affirmed on causation in an unpublished opinion and did not reach the Garcetti ground, and the petition itself concedes the cited split is "not quite posed as it is here." The anchor also uses the current Term's live 3.9% reached figure rather than a prior-Term pool, a defensible forward-cell choice given the table's caption, but it carries the thinnest, most censored row of the table without saying so. Nothing in the document is wrong; it is simply a short docket-signal argument that would have been equally plausible had the case been a strong vehicle. Hence 0.5: sound direction, little discriminating analysis.

## Leakage

Mode `forward`. The prediction was created September 17, 2026, eleven days before the conference and eighteen before the denial, so no disposition existed to retrieve. The log's `result_capture_coverage` is 0.0, so every call was graded on its query: provisioned record reads, the statpack, and three generic corpus queries naming no caption or docket. No web search, no CourtListener call, no read under `data/qp-topics/`. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. No evidence of a decided case provisioned forward.

## Big case

My independent read is 0.2 (see `big_case.notes`). The predictor's own score sits in the staged `prediction.json`, so it was visible when I read the record; the read above is my own, formed from the posture, the waiver, and the silent denial.
