# Evaluation — codex-baseline — scotus/9026000121 — evt-petition-arrival-disposition

**Stage:** cert (petition, arrival moment). **Outcome:** denied on 2026-10-05 after respondents waived and the petition was distributed once for the 2026-09-28 conference; no noted dissent. `actual_granted = 0`.

## Quantitative

- `correct = 1` — `predicted_disposition: denied` matches `actual_disposition: denied`.
- `brier_score = 0.000036` — `(0.006 − 0)²`.
- `segment_base_rate`, `brier_skill_score`: **omitted**, `base_rate_basis` null. The prediction froze `context.band = baseline` under `context.salience_version = sal-v3`, but the committed `metrics/statpack.md` band table is headed **sal-v4** ("Segment base rate by salience band (sal-v4)"). A band name only means something under the version that assigned it, so the table is no baseline for this band; per the contract the only answer is to omit the rate and the skill score together and record the mismatch in `flags.json`. I did not relabel to `terminal`. For the reader: the sal-v4 table's baseline bracketed `reached` figures over OT2017–OT2025 run 3.9%–5.9%, which is not the 6.56% sal-v3 anchor the candidate pooled at prediction time; the two are not comparable, which is the point of the omission.
- `vote_accuracy`: omitted (cert cell; votes are never scored off the merits stage).
- `judgment_correct`: null (no judgment on either side).
- `claim_scores`: not mine; left absent for the harness.

## Reasoning quality: 0.80

What the rationale does well:

- Picks the right anchor for an arrival cell (the weakest band's bracketed `reached` rate, not the terminal rate) and says why.
- The downward adjustments are specific and accurate to the petition: no split alleged; the federal hook rests on a contested factual predicate (the Appellate Court of Maryland found a LinkedIn post insufficient to show the retired judge was practicing law when he signed the order, and the petition's own footnote concedes the order may have issued "a few days before" the judge began county work); the case arrives through an unreported intermediate opinion and a procedural dismissal (Md. Rule 8-602) by the Supreme Court of Maryland, which the petition itself has to argue is not an adequate and independent state ground. QP2 is correctly read as a state-law error-correction request (Md. Rule 2-703 fee memoranda after *Sugarloaf*).
- Names its main evidentiary gap honestly: no brief in opposition at arrival. (The respondents in fact waived.)

What holds it below the top:

- The move from a ~6.5% anchor to 0.006 is a tenfold cut stated as a conclusion; the rationale does not say why 0.006 rather than 0.01–0.02, nor does it name the one feature that cuts the other way (an extreme-facts judicial-bias claim is the shape of the occasional summary per curiam). Given the outcome the number was well placed, but the calibration step is the thinnest part of the document.
- The conditional summary-route reasoning (vacatur for *Sugarloaf*) is a thoughtful counterfactual but the document gives it more space than the headline calibration.

Scored on `reasoning.md` only. The forecast document (`predicted_reasoning.md`) was read for context and is not scored; it forecast one distribution, no relist, no CVSG, and a silent denial, which is what happened.

## Leakage

`mode = forward`, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. The log (17 calls, all captured) is shell reads of the provisioned record, the prompt, the schema and the committed statpack; the one call collapsed to `other` carries only harness-redacted text, which is removed text and not outcome material. No web search, no CourtListener call, no corpus query, no read under `data/qp-topics/`, no `retrieved_doc_date` anywhere. The prediction was created 2026-08-16 with the docket at the response-due stage; the distribution (2026-09-09) and denial (2026-10-05) came later. I checked for a decided case provisioned forward and found none.

## Big-case read

`evaluator_score = 0.05`. A private Maryland fee dispute with a novel but factually unproven judicial-eligibility due-process angle; no split, unreported decision below, procedural dismissal by the state high court, waiver, one distribution, silent denial, no amici. Formed from the docket, the petition, and the outcome. The staged `prediction.json` places the predictor's own `big_case_score` in view when the file is read, so I note that; my read rests on the record, not on that number.
