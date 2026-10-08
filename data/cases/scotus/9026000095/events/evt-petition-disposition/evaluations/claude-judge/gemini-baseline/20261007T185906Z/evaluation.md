# Evaluation — gemini-baseline

**Cell:** cert stage, forward mode. Outcome: petition **denied** on 2026-10-05 at its first conference (one distribution, no relist, no CVSG, no noted dissent).

## Quantitative

- `predicted_disposition` = `denied` vs `actual_disposition` = `denied` → `correct` = 1.
- `probability` = 0.005, `actual_granted` = 0 → `brier_score` = 0.000025.
- `segment_base_rate` = 0.0501, basis `risk_set`: the prediction's frozen context carries `band: baseline` **and** `salience_version: sal-v4`, matching the statpack's sal-v4 band-table heading. Pooled bracketed `reached` figure for `baseline` over OT2017–OT2025, resolved-weighted by the bracketed `n` (12,720), ≈5.01%. The caption renders 10 of 10 Terms, so no lookback divergence.
- `brier_skill_score` = 1 − 0.000025 / 0.0501² ≈ 0.9900.
- No `vote_accuracy`, `judgment_correct`, or `semantic_grades`: cert cell. `claim_scores` is the harness's.

## Reasoning quality — 0.55

The document is two short paragraphs. What it gets right:

- It names the correct anchor family ("roughly 4–6%, the bracketed `reached` rate" for a paid baseline petition), which is the right table and the right figure, though it does not pool or state a number.
- Its three adjustments are the right ones and each is borne out: pro se status; the BIO's preservation and independent-state-ground points (timeliness and sufficiency under California law); and adverse rulings as insufficient under Caperton.
- The headline call and the ancillary expectations (no relist, no CVSG) were all correct.

What holds it down:

- Thin sourcing and no adversarial framing. It says the BIO "persuasively notes" the federal claim was not preserved, but the petition says the opposite and the candidate had no reply or lower-court filings to arbitrate; the other side's account is adopted as fact rather than priced as a contested assertion.
- It omits the two most concrete vehicle problems in the record: the section 1257 finality bar (the nuisance action is still pending, and the BIO leads with it) and the mismatch between the QP's "without any reasoned analysis" premise and the six-page reasoned trial-court order. It also makes nothing of the docket signals available on the snapshot: the stay application denied by a single Justice and then by the full Court without dissent, and the passed September 28 conference with no relist posted.
- Listing "the California Supreme Court has already denied discretionary review" as a factor adds nothing, since that is simply the posture in which every such petition arrives.
- The jump from a 4–6% anchor to 0.5% is asserted ("adjust downwards significantly") with no intermediate reasoning about magnitude.

The analysis is directionally sound and not wrong anywhere I can identify, but it is a sketch of the case rather than an analysis of it, and a reader could not reconstruct why 0.5% rather than 2% or 0.1%.

## Big case

My own read is 0.03: a pro se, interlocutory recusal dispute arising from a city's short-term-rental enforcement action, no split, no amicus, no institutional petitioner, stay denied twice without dissent, denied at first conference without noted dissent. The predictor's 0.01 is close to that read; I supply only my read, not an agreement number.

## Leakage

Forward mode, `not_applicable`. See `leakage.notes`: every logged call is a read of provisioned or repository inputs, and the log's zero capture coverage is the engine's standing shape rather than a defect, so each row is graded on its query. `retrieved_outcome_material` = false; `leakage_suspected` = false.
