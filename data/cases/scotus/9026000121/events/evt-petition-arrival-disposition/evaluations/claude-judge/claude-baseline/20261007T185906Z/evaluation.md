# Evaluation — claude-baseline — scotus/9026000121 — evt-petition-arrival-disposition

**Stage:** cert (petition, arrival moment). **Outcome:** denied on 2026-10-05 after respondents waived and the petition was distributed once for the 2026-09-28 conference; no noted dissent. `actual_granted = 0`.

## Quantitative

- `correct = 1` — `predicted_disposition: denied` matches `actual_disposition: denied`.
- `brier_score = 0.0004` — `(0.02 − 0)²`.
- `segment_base_rate`, `brier_skill_score`: **omitted**, `base_rate_basis` null. The prediction froze `context.band = baseline` under `context.salience_version = sal-v3`; the committed `metrics/statpack.md` band table is headed **sal-v4**. A band name only means something under the version that assigned it, so the table is no baseline for this band and the contract's only answer is to omit rate and skill together and flag the mismatch (`flags.json`). I did not relabel to `terminal`. The candidate's own ~6.5% pooled anchor was computed from the sal-v3 table in force when it ran; the sal-v4 table now rendered shows baseline `reached` figures of 3.9%–5.9% over OT2017–OT2025, so its arithmetic cannot be checked against the committed pack and is not scored.
- `vote_accuracy`: omitted (cert cell).
- `judgment_correct`: null.
- `claim_scores`: not mine; left absent for the harness.

## Reasoning quality: 0.85

The soundest of the three rationales:

- The anchor section states what population the bracketed `reached` figure is, why an arrival cell uses it, and which Term rows were pooled, and then marks the pooled number as approximate with its per-Term spread. That is the right epistemic posture for a hand-pooled baseline.
- Five adjustments, each tied to a verifiable feature of the petition: no split (quoting the petition's own "Question of First Impression" and "no controlling Supreme Court precedent" language, both present in the staged text); the state-law predicate under Md. CJP § 1-302 that the Maryland courts resolved against the petitioner; QP2 as a non-federal question the Court cannot review; presentation quality; and the originating-court rate for state high-court petitions.
- It names the one upward feature (an extreme-facts judicial-bias claim can draw a summary per curiam, cf. *Rippo v. Baker*) and explains why that keeps it off the terminal floor without approaching the arrival average. A rationale that argues both directions and then lands is more credible than one that only argues down.
- The uncertainty section is specific: it has not read the Supreme Court of Maryland's decision, so the vehicle reading is inferred from an advocate's framing, and it says which way the error would run. It also correctly discounts the linked application 25A1252 as the extension already on the docket.

What holds it off the top: 0.02 was, given the outcome, a little generous against a petition that drew a waiver and a silent first-conference denial, and the rationale's stated reason for not going lower (the *Rippo* shape) is weaker than it is presented, since *Rippo* involved an undisclosed conflict actually established on the record, while here the predicate was found unproven. That is a calibration quibble, not an analytical error.

Scored on `reasoning.md` only. The forecast document was read for context and is not scored; for the record it forecast a waiver, one distribution for the long conference, and an early-to-mid October silent denial, which is exactly the docket's course.

## Leakage

`mode = forward`, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. The log (26 calls, all captured) is reads of the provisioned inputs, the prompt, the schema and the statpack, plus one corpus `query` on the *Caperton* citation (556 U.S. 868), a lookup about an authority rather than this docket; the candidate's `retrieval.md` reports it returned no rows with its `ranged corpus reads` line. No web search, no CourtListener call, no read under `data/qp-topics/`, no `retrieved_doc_date` on any call. The prediction (2026-08-16) predates the distribution and the denial, and its docket facts are the arrival-time entries. No sign of a decided case provisioned forward.

## Big-case read

`evaluator_score = 0.05`. A private Maryland fee dispute with a novel but factually unproven judicial-eligibility due-process angle; no split, unreported decision below, procedural dismissal by the state high court, waiver, one distribution, silent denial, no amici. Formed from the docket, the petition, and the outcome. The staged `prediction.json` places the predictor's own `big_case_score` in view when the file is read; my read rests on the record, not on that number.
