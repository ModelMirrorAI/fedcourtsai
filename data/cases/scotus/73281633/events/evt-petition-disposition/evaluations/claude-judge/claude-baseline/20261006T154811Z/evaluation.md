# Evaluation of claude-baseline — scotus/73281633, evt-petition-disposition

**Cell:** cert stage, forward mode. **Outcome:** petition DENIED on 2026-10-05 after a single distribution (Conference of 9/28/2026), no CVSG, no relist, no noted dissent (`actual_granted` = 0).

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.11 − 0)² = 0.0121.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`; the committed statpack's "Segment base rate by salience band (sal-v4)" heading matches, so the bracketed `reached` figure applies, pooled resolved-weighted over the rendered Terms strictly before OT2025 (2017–2024): 593 / 11,580 ≈ 5.12%. The caption renders 10 of 10 Terms, so no lookback divergence.
- `brier_skill_score` = 1 − 0.0121 / 0.0512² = −3.62. Negative, as for every candidate: the forecast sat above the baseline and the petition was denied.
- No `vote_accuracy`, no `semantic_grades`: cert stage.

## Reasoning quality: 0.84

The strongest of the three analyses, and the one whose structure most closely tracks why the petition was denied.

- **Anchor and cross-checks are correct.** Same sal-v4 pooling to ~5.1%, with the relist `0` bucket explicitly read as a terminal figure that understates a live petition, the CVSG `none` bucket and the CA2 row used as background only. That is the statpack read the way its captions ask.
- **The largest discount is the right one.** It names the interlocutory posture as "the single largest discount," then separately names the alternative grounds below as a "classic vehicle defect" that leaves the questions non-outcome-determinative. The appendix bears the public-interest ground out: the Second Circuit held that even if the First Amendment claims had likely merit the district court's public-interest assessment was not an abuse of discretion (Pet. App. 30a). One overstatement: it says the Second Circuit "affirmed on those grounds too," plural, including delay, but footnote 9 of the panel opinion says the court need not address the delay question; only the public-interest ground was reached on appeal. The conclusion survives the correction, since one independent ground is enough; codex-baseline read this footnote correctly.
- **The split is tested, not assumed.** It credits the BIO's account that the panel cited studies and stated the Edenfield standard, and reads the other circuits as saying common sense *can* suffice rather than must — "a Justice looking for a clean legal question can fairly say there is none here yet." That is the reading that explains a quiet denial.
- **Doctrinal climate is used sensibly.** Free Speech Coalition v. Paxton (intermediate scrutiny, deference on means, minors) and the Court's long non-engagement with Central Hudson's rigor are relevant and pointed the right way.
- **It checked what it could.** The CourtListener lookups ruled out an intervening decision (no GVR hook) and a companion or hold candidate, which is exactly what the summary-disposition and relist estimates needed.
- **Calibration is explicit and bounded**: "not above 0.18 without a relist … not below 0.06 given the amici," and a "where to discount me" section that names the unread reply and the parties'-eye view of the split. The realized outcome sat inside the stated reasoning.

Held back by: the delay overstatement above; the split and alternative-ground claims rest on the briefs rather than the cited circuit opinions, as it acknowledges; and the 0.32 relist estimate is a little high for a petition the Court disposed of on the first conference, though the reasoning for it (amici plus a state respondent at the Long Conference) was fair ex ante.

## Big case

My own read is 0.38 (see `evaluation.json`); the predictor's score was in the staged `prediction.json`, so I had seen it before writing mine, and my read is formed on the record and outcome rather than on it. claude-baseline's 0.45, "doctrinal rather than headline," is the closest of the three to mine and its rationale gives the same reasons.

## Leakage

Forward cell, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. Prediction created 2026-09-16; denial 2026-10-05. The fully captured log (38 calls) shows one CourtListener docket item for this docket returning `date_modified` 2026-07-01 and no termination date (retrieved document date 2026-04-02, the filing), two Central Hudson searches whose latest document date is 2026-03-31 (Chiles v. Salazar), and two corpus queries (47 GETs / 12.3 MB, then a warm cache). Every retrieved date precedes resolution; the docket lookup confirmed the case was still open, which is the opposite of leakage. No `data/qp-topics/` read. No sign that a decided case was provisioned forward.
