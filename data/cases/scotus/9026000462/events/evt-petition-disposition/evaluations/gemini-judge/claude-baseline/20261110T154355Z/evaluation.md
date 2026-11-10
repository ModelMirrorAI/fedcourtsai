# Evaluation of `claude-baseline` (`scotus/9026000462`, `evt-petition-disposition`)

## Quantitative summary

- **Stage:** `cert` (discretionary petition for writ of certiorari, `moment: distribution`)
- **Predicted disposition / probability:** `denied`, `P(grant) = 0.006`
- **Actual outcome:** `denied` (`actual_granted = 0`) on `2026-11-09`
- **Correct:** `1`
- **Brier score:** `0.000036`
- **Segment base rate & skill score:** Left null for harness stamping against the stamped segment base rate.

## Analysis of `reasoning.md` (`reasoning_quality = 0.95`)

`claude-baseline` delivered an outstanding analysis under difficult input conditions. When the prediction ran on October 8, 2026 (`run_id: 20261008T143010Z`), the provisioned `petition.txt` had `empty_text: true` (prior to the October 18 OCR pass) and no `questions-presented.txt` was available. Rather than stopping at the blank text, `claude-baseline` queried CourtListener's RECAP dockets and docket entries for the Northern District of Iowa (`2:23-cv-01033`, docket ID `68013931`) and the Eighth Circuit (`25-2561`) and reconstructed the exact factual and procedural posture below: a pro se former employee's ADA employment discrimination action against Honkamp Krueger & Co., P.C., dismissed with prejudice on June 2, 2025 as a Fed. R. Civ. P. 37(b)(2) discovery sanction (plus a $500 monetary sanction) after the plaintiff violated a discovery order, summarily affirmed by the Eighth Circuit on March 23, 2026, with post-judgment Rule 60 motions denied on August 10, 2026. Checking `claude-baseline`'s reconstruction against the subsequently OCR'd `petition.txt` and `questions-presented.txt` confirms that `claude-baseline` identified the exact questions and grievances at issue.

For its base-rate anchor, `claude-baseline`'s use was graded against statpack build `1c4f550b7b75` (`sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, the `sal-v4` build in force at `20261008T143010Z`, rebuilt via `fedcourts statpack-at`, rather than the currently committed `sal-v8` statpack). `claude-baseline` properly anchored on the `sal-v4` `baseline` band's bracketed `reached` (risk-set) rate pooled across strictly prior Terms (OT2017–OT2025), matching the stamped segment base rate methodology, and justified its downward adjustment to `0.006` by citing the pro se posture, the fact-bound abuse-of-discretion standard governing Rule 37 discovery sanctions, the respondent's same-day waiver, and the absence of any circuit split or intervening decision.

`claude-baseline` also spotted the key procedural detail on the Supreme Court docket: the frozen `distribution_count: 1` (the September 9, 2026 distribution for the September 28 Long Conference) carried the linked motion `26M22` for leave to file a supplemental appendix under seal (granted October 5), whereas the cert petition itself was docketed on October 7 with a same-day response waiver. From that sequence, `claude-baseline` rightly inferred (`relist-increment: 0.97`) that the petition would receive one additional distribution entry for its initial cert conference consideration before being denied without a true relist. The only minor weakness in `reasoning.md` is assigning `0.75` to `summary-disposition-route` conditional on a grant while simultaneously noting that no intervening decision or clear error supported a summary order.

## Predicted reasoning (`predicted_reasoning_quality = 0.95`)

`claude-baseline`'s `predicted_reasoning.md` made specific, discriminating central claims that were completely borne out by the subsequent record:

1. **Silent denial at the petition's first cert conference (`borne-out`):** `claude-baseline` forecast that the Court would deny the petition without separate writing at the first conference for which the petition itself was distributed. The petition was denied on November 9, 2026 with `noted_dissent_from_denial: false`.
2. **One additional distribution entry due to the `26M22` sealing-motion sequence, and no further relists (`borne-out`):** `claude-baseline` specifically explained that because the September 9 distribution covered motion `26M22` (granted October 5) prior to the October 7 docketing, the petition would be distributed once more in October for an early-to-mid-November conference and denied on the following Monday order list without any further relist. In fact, the petition was distributed once more on October 14, 2026 for the November 6, 2026 conference (`signals.distribution_count: 2`) and denied on Monday, November 9, 2026.
3. **No call for a response and no CVSG (`borne-out`):** `claude-baseline` forecast that the Court would not request a response after respondent's October 7 waiver and would not issue a CVSG (`0.002`). Neither occurred.
4. **Summary disposition conditional on a grant (`unresolved`):** Conditional on a grant, `claude-baseline` favored a summary order (`0.75`); because cert was denied, this conditional claim was never tested.

## Leakage assessment

- **Mode:** `forward` (predicted `2026-10-08T14:52:59Z`; resolved `2026-11-09`).
- **Assessment:** All 24 tool calls in `retrieval_log.json` are `captured` (`result_capture_coverage: 1.0`). None retrieved post-cutoff or outcome-revealing material for this case (the latest `retrieved_doc_date` is `2026-08-10` from the N.D. Iowa docket). `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`.
