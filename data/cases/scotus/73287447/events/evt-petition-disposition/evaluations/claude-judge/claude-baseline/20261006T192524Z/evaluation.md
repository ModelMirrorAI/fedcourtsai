# Evaluation: claude-baseline — scotus/73287447, evt-petition-disposition

**Cell type:** cert stage (`event.yaml` stage `cert`, moment `distribution`), forward mode. Outcome: petition **denied** on 2026-10-05 (`actual_granted` = 0, no noted dissent from denial, `distribution_count` 2, no CVSG).

## Quantitative

| field | value |
| --- | --- |
| predicted_disposition / actual | `denied` / `denied` → `correct` = 1 |
| probability | 0.13 |
| brier_score | 0.0169 |
| segment_base_rate | 0.1724 (`risk_set`) |
| brier_skill_score | 0.4314 |

**Base rate.** The prediction's frozen `context` carries `band: elevated` **and** `salience_version: sal-v4`, and the statpack's "Segment base rate by salience band" table is headed `sal-v4`, so the `risk_set` basis applies. I pooled the bracketed `reached` figure for `elevated` over every rendered Term strictly before this case's Term (2025), i.e. OT2017–OT2024, resolved-weighted: 484.4 / 2810 ≈ 0.1724. The table renders 10 of 10 Terms, so the rendered window is the whole pack and there is no lookback divergence to flag. The baseline's Brier against a denial is 0.1724² ≈ 0.0297.

## Leakage

Forward cell. The prediction was written 2026-09-18 from the 2026-09-17 snapshot; the petition was then distributed for the 2026-09-28 conference and was not decided until 2026-10-05, so the case was genuinely open and ordinary retrieval could not leak an outcome that did not exist. Its log (28 calls, capture coverage 1.0) shows the only this-case lookup was a CourtListener docket-item read returning `date_filed` 2026-05-01 and a null `date_terminated`, plus a docket-entries call that returned nothing; web searches surfaced only pre-snapshot trade-press coverage of the petition and BIO and a 2024 DOJ amicus brief filed in the Second Circuit. Nothing dated at or after the resolution. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My own read, 0.35 (see `big_case.notes`): a real but narrow antitrust-standing question, interlocutory, no amici, denied silently.

## Reasoning quality: 0.85

**What it got right.** The anchor is exactly the one the evaluator scores against (0.172 pooled over the eight prior Terms, correctly excluding the case's own Term), and the write-up says so. The downward adjustments are the ones a cert-stage reader would weigh and they all bore out: the interlocutory posture (reversal of a dismissal, case back in discovery); the collapse of the asserted 2-1 split into a disagreement over applying a shared multi-factor test, with the comparator circuits having disclaimed any bright-line rule; the absence of any cert-stage amicus for a petition claiming cross-industry stakes; and the fact-bound shape of the merits argument. The strongest independent contribution is retrieving and locally extracting the DOJ Antitrust Division's July 2024 Second Circuit amicus brief and drawing the right inference from it: the government is already on the doctrine's respondent side, so a CVSG would likely return a deny recommendation, which both lowers the grant number and caps the CVSG claim. The upward factors (response request after waiver, a published split-panel decision with a substantial dissent, sophisticated counsel) are stated and weighed rather than ignored, and the document correctly notes that the band already prices in the response request. It also correctly reads the two distributions as one mooted June distribution plus a first real consideration, rather than a classic relist.

**Where it is weaker.** The reading of the comparator circuits' qualifications came from the BIO's characterization rather than the opinions themselves; the document owns this in its "where to discount me" section and points to the petition's own quotation of Montreal Trading as corroboration, which is a fair mitigation but not the primary-source check that was available. The corpus queries it ran returned nothing comparable and it says so plainly, which is honest rather than padded. The final number, 0.13, sits a little below the anchor and well above the paid-docket rate; given the outcome and the no-relist, no-writing path the Court actually took, the calibration reads as sound rather than lucky.

Both the claims block and `predicted_reasoning.md` are unscored here per the contract; I read the forecast document only for context on how the number was formed.
