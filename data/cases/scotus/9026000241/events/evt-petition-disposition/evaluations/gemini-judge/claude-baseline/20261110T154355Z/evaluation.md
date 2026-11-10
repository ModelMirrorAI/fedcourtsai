# Evaluation of `claude-baseline`

## Overview and Quantitative Summary

- **Case / Event:** `scotus/9026000241` (*Fred Rahdar, et al. v. City of Friendswood, Texas, et al.*, No. 26-241) / `evt-petition-disposition` (stage: `cert`)
- **Outcome:** `denied` (`actual_granted = 0`) on `2026-11-09`, with `signals.distribution_count = 1`, `signals.cvsg_date = null`, and `noted_dissent_from_denial = false`.
- **Prediction:** `predicted_disposition = "denied"`, `granted = 0`, `probability = 0.005`.
- **Scores:** `correct = 1`, `brier_score = 0.000025`, `reasoning_quality = 0.88`, `predicted_reasoning_quality = 0.85`.

## Statpack Provenance and Leakage Audit

- **Statpack build graded against:** `claude-baseline` ran in `20261013T143156Z` under salience version `sal-v4`. Reconstructing the statpack in force at prediction time via `uv run fedcourts statpack-at` resolves to build `a14b36a1e190a86d6a01df2ce410f5f9e54fb98b` (`sha256:84a5c25d4bf0a2a70ba5c6e9392e2e21d43ed5b794de0ae59c27cf1973ad0e7e`), rather than the currently committed `sal-v8` pack. All base-rate references in `claude-baseline`'s rationale were verified against build `a14b36a1e190` (`sal-v4`), and the cell's formal baseline is the stamped segment base rate.
- **Leakage assessment (`not_applicable`, `leakage_suspected: false`):** This was a forward prediction (`mode: "forward"`, `created_at: 2026-10-13T14:43:09Z`) placed weeks before the November 9, 2026 denial. Inspection of `retrieval_log.json` and `retrieval.md` confirms that `claude-baseline` read only the local provisioned case record and `metrics/statpack.md`, with no external queries and no outcome leakage.

## Rationale Assessment (`reasoning_quality`: 0.88)

`claude-baseline` delivered a crisp, well-calibrated, and legally sound analysis in `reasoning.md`:

1. **Base-Rate Anchoring and Calibration:** Checked against the `a14b36a1e190` (`sal-v4`) statpack in force at prediction time, `claude-baseline` accurately cited the `baseline` salience band's reached figures across strictly prior Terms 2017–2025 (corresponding to the stamped segment base rate) as well as the zero-relist paid-petition reference cut, and clearly explained why most grants in the `baseline` risk set come from petitions that later draw a call for a response or relists. Adjusting downward from the stamped segment base rate to `p = 0.005` was well justified by the waived response and vehicle defects.
2. **Procedural and Vehicle Analysis:** `claude-baseline` accurately identified the four key drivers of denial: (a) respondents waived the right to respond on September 29, 2026 and the petition went straight onto the November 6, 2026 conference list with no call for a response; (b) the Fifth Circuit decided the appeal in a short, unpublished per curiam opinion on the summary calendar and held petitioners' *Nieves*-exception comparator and officer-testimony arguments forfeited because they were raised for the first time on appeal; (c) an unpublished affirmance resting on forfeiture creates no genuine split with *Murphy v. Schmitt* (8th Cir. 2025), and the Question Presented is framed as fact-bound error correction under *Gonzalez v. Trevino*, 602 U.S. 653 (2024); and (d) *Gonzalez* (2024) predates the March 2026 Fifth Circuit opinion and was cited below, eliminating an intervening-decision GVR rationale.
3. **Minor Omissions:** `retrieval_log.json` shows `claude-baseline` read only the first 9,000 non-blank characters of `appendix.txt` (covering the Fifth Circuit opinion at App. 1a–6a and the district judge's adoption order, stopping before the magistrate judge's M&R at App. 12a–35a), even though `reasoning.md` lists "the district court's memorandum and recommendation" under "Inputs read." As a result, it did not address whether the 12-year arrest-record statistics discussed in the M&R (App. 27a–31a) were preserved, nor did it verify the procedural posture of *Murphy v. Schmitt* via CourtListener.

## Predicted reasoning (`predicted_reasoning_quality`: 0.85)

`predicted_reasoning.md` is cleanly organized around the headline forecast and the five cert-stage topics:
- **Central claims borne out:** `claude-baseline` led with a specific call that the petition would be denied on the order list immediately following its first conference (November 6, 2026) with zero further distributions, no CVSG, and no noted dissent from denial. All three observable claims were borne out by the November 9, 2026 order list (`actual_disposition = "denied"`, `distribution_count = 1`, `cvsg_date = null`, `noted_dissent_from_denial = false`).
- **Conditional claims (`unresolved`):** Its conditional calls on Question Presented reformulation and summary disposition were grounded in the record and remain `unresolved` given the denial. A small deduction reflects a slight internal tension between `predicted_reasoning.md` stating that a grant "would most likely be a summary vacatur in the style of *Gonzalez*, not plenary review" and `prediction.json` recording `summary-disposition-route: 0.30` (which implies 30% summary vs. 70% plenary conditional on grant).
