# Evaluation: gemini-baseline — scotus/73500242, evt-petition-disposition

## Outcome and scoring

Cert-stage cell, forward mode. The petition (No. 25-1340, Nwosu v. 1600 West Loop South) was distributed once, for the September 28, 2026 conference, and denied on October 5, 2026 with no noted dissent. `actual_disposition` = `denied`, `actual_granted` = 0.

- **Disposition:** predicted `denied`, actual `denied` → `correct` = 1.
- **Brier:** probability 0.02 → (0.02 − 0)² = **0.0004**.
- **Segment base rate (`risk_set`):** the prediction froze `band: baseline` under `salience_version: sal-v4`, and the statpack's "Segment base rate by salience band" table is rendered under sal-v4, so the risk-set basis applies. Pooling the baseline band's bracketed `reached` figures, resolved-weighted, over every rendered Term strictly before the case's Term (OT2025), i.e. OT2017–OT2024 (11,580 weighted resolved), gives **0.05121** (593.0 / 11,580 from the unrounded `metrics/statpack.json` rows; the rendered percentages give 0.05120). The table renders "most recent 10 of 10 Terms", so the rendered window is the whole pack and matches the configured ten-Term lookback; no window divergence to flag.
- **Brier skill:** baseline Brier = 0.05121² = 0.002622; 1 − 0.0004 / 0.002622 = **0.847**.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: not applicable on a cert cell; omitted or null.

## Reasoning quality: 0.60

The analysis reaches the right place for the right general reasons, but it is thin, and one of its numbers is not reasoned at all.

What it got right:

- **Anchor.** It names the baseline band and the pooled `reached` rate of about 5.1 percent over OT2017–OT2024, which is the right figure under the right basis, though it shows no working.
- **Core diagnosis.** Error correction of a summary-judgment ruling without a recurring systemic issue, and a petition that claims a lack of consensus rather than a square split, are the two things that mattered, and both are stated correctly. The CVSG reasoning (private parties, no federal interest) is right.

Where it falls short:

- **No engagement with the record beyond the petition's framing.** The write-up never says what the Fifth Circuit held, that the decision is unpublished, that no brief in opposition was filed, or that the Court distributed without calling for a response. Those are the facts that place this petition at the bottom of the baseline band rather than merely in it, and the predicted number (2 percent, roughly a 60 percent cut from the anchor) is asserted rather than built from them.
- **Dissent from denial at 0.15 is unsupported.** The document offers one clause for it ("possible but unlikely") and nothing else. Separate writings on denial attach to a very small fraction of paid denials, and the candidate's own description of the vehicle (fact-bound, poor, contested facts) argues against a writing, not for one. The number is inconsistent with the reasoning that surrounds it. This is not a scored claim here, but it is part of the rationale document and it reads as a number chosen rather than reasoned.
- **Length.** Two paragraphs is enough for a correct call on an easy case, which this was; it is not enough to show that the predictor would have noticed if the case were harder.

I did not score `predicted_reasoning.md` or the claims block.

## Leakage

Mode `forward`, so the default is `not_applicable`. I checked rather than stamped it: the prediction was created 2026-09-18, seventeen days before the denial. Every row in the log is `unobserved` (`result_capture_coverage` 0.0, an engine's standing shape rather than a defect), so each call was graded on its query: provisioned-record reads, one CourtListener docket search for 25-1340, one corpus query for docket 73500242, and a statpack read. All ran before the conference, so none could have returned a disposition that did not yet exist. No web search, no read under `data/qp-topics/`. The reasoning cites nothing outside the provisioned record and the statpack. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big-case read

My independent read is 0.08: a single-plaintiff, fact-bound section 1981 restaurant case on an unpublished per curiam, with no opposition, no amici, and a silent denial. The statutory question has some doctrinal interest but this vehicle carried none of it to the Court.
