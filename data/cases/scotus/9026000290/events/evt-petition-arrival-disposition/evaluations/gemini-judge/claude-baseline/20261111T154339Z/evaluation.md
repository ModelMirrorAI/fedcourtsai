# Evaluation of `claude-baseline`

## Overview and Outcome

- **Case:** *Mihal Emberton v. Superior Court of California, City and County of San Francisco, et al.*, No. 26-290 (`scotus/9026000290`)
- **Event:** `evt-petition-arrival-disposition` (`stage: cert`, `moment: arrival`)
- **Outcome:** Petition `denied` on November 9, 2026 (`actual_granted: 0`, `distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`).
- **Prediction:** `predicted_disposition: denied`, `probability: 0.004` (`correct: 1`, `brier_score: 0.000016`).

## Quantitative and Base-Rate Assessment

`claude-baseline` predicted `denied` with `P(grant) = 0.004`, earning `correct = 1` and a Brier score of `0.000016`. Per the cert-stage evaluation contract, `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left null here for the harness (`stamp-cell`) to stamp from the stamped segment base rate.

To check `claude-baseline`'s base-rate reference against the statpack in force at prediction time (`20260927T182226Z`), I rebuilt that statpack using `fedcourts statpack-at` (commit `2420d5dd72e1`, digest `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`). `claude-baseline` pooled the `sal-v4` `baseline` bracketed `reached` rates across prior Terms OT2017–OT2025, arriving at ~5.0% over ~12,700 weighted petitions, and properly noted why the terminal `relist-0` figure (1.2% granted) must not be used as an arrival anchor.

## Reasoning Quality (`0.95`)

`reasoning.md` is crisp, well-structured, and grounded in specific details from the petition and snapshot (`reasoning_quality = 0.95`):

- **Base-rate and structural clarity:** Properly anchors on the ~5.0% `sal-v4` `baseline` risk-set floor over ~12,700 weighted petitions and highlights the structural composition issue that the paid `baseline` segment pools pro se paid petitions with counseled ones.
- **Doctrinal and vehicle analysis:** Accurately observes that the questions presented posit an internal conflict among the Court's own cases (*Ciraolo*/*Dow*/*Marshall* vs. *Katz*/*Kyllo*/*Horton*/*Boyd*) rather than a lower-court split, and explains why existing doctrine reconciles them (visual observation of an unenclosed front yard from a public vantage point is not a search). Notes the one-page summary writ denial by the California Court of Appeal following a sustained demurrer to a seventh amended complaint, the prior 2023 federal dismissal on the pleadings, the sprawling list of unrelated statutory citations in the petition, and the minor cover-vs-snapshot lower-court naming discrepancy.

## Predicted reasoning (`0.95`)

`predicted_reasoning.md` is an exceptionally sharp and specific forecast of the petition's trajectory (`predicted_reasoning_quality = 0.95`). Beyond calling the denial without argument or separate writing and no CVSG, it specifically forecasts that following the October 5, 2026 response due date, the respondent would not file a brief in opposition and the petition would be distributed once for a late-October or early-November 2026 conference and denied in the following order list by mid-November 2026 with zero relists. That exact sequence occurred: no response was filed, the petition was distributed once on October 21, 2026 for the November 6, 2026 conference, and the Court denied certiorari on November 9, 2026.

## Leakage Assessment

- **Mode:** `forward` (prediction run `20260927T182226Z`, created `2026-09-27T18:40:00Z`; distributed `2026-10-21`; resolved `2026-11-09`).
- **Assessment:** `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. The case was unresolved when predicted. `retrieval_log.json` shows local shell/file reads of the provisioned inputs and statpack, plus two generic `fedcourts query` calls for 2020s SCOTUS priors (`ranged corpus reads: 11 GET(s), 2752512 byte(s)` and `0 GET(s), 0 byte(s)`) logged in `retrieval.md`.
