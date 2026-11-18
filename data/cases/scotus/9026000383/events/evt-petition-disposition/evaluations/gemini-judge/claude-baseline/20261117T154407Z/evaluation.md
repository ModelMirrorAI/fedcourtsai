# Evaluation of `claude-baseline` — *Felicia Scroggins v. City of Shreveport, Louisiana* (`scotus/9026000383`, `evt-petition-disposition`)

## Outcome and Quantitative Summary

- **Stage / Moment:** `cert` / `distribution`
- **Outcome:** Certiorari `denied` on `2026-11-16` (`actual_granted = 0`, `distribution_count = 1`, `cvsg_date = null`, `noted_dissent_from_denial = false`).
- **Prediction:** `predicted_disposition = "denied"`, `probability = 0.004` (`correct = 1`, `brier_score = 0.000016`). The stamped segment base rate and Brier skill score are computed by the harness over the prediction's frozen `baseline` band (`risk_set`).

## Assessment of `reasoning.md` (`reasoning_quality = 0.76`)

`claude-baseline` delivered a concise, well-calibrated procedural rationale that reached the right disposition and probability range for valid structural reasons, while leaving substantive depth on the table by skimming only the opening of the provisioned filings.

**What worked well:**
- **Base-rate discipline:** Verified against the `sal-v4` statpack build in force when `claude-baseline` ran (`sha256:063aea1961d5833e02e3aa0254477260a34f98f23a2751a1620aaf7c8db03726`, commit `1913c7a1172a` prior to the later `sal-v8` refresh), `claude-baseline` accurately separated its frozen `baseline` risk-set anchor from the terminal `baseline` band and zero-relist cuts, and gave a sound procedural justification for stepping well below the stamped segment base rate.
- **Procedural posture:** Correctly identified the decisive docket signals at the distribution moment—a pro se petitioner on the paid docket, Respondent City of Shreveport's October 10 waiver of its right to respond, distribution on October 28 for the November 13 conference without a call for a response, zero amicus support, an unpublished Fifth Circuit affirmance, and the absence of any asserted circuit split.
- **Epistemic candor:** Explicitly disclosed in `reasoning.md` that it did not verify the lower-court record beyond the petition's opening description.

**Where the analysis fell short:**
- **Incomplete reading of provisioned record:** As reflected in `retrieval_log.json` and `reasoning.md`, `claude-baseline` read `questions-presented.txt` and only the first 60 lines of `petition.txt`, and did not read `appendix.txt` at all. Consequently, it missed concrete, case-dispositive vehicle barriers documented in the district court's ruling in `appendix.txt`: (1) Petitioner missed 1,153 of 1,779 available shifts (64.6%) over five years and reported ongoing PTSD triggers and inability to resume full Fire Engineer duties at her fitness-for-duty evaluation and pre-disciplinary conference; (2) the district court rested summary judgment on an *independent alternative holding* under *McDonnell Douglas* (failure to show pretext for the City's legitimate, nondiscriminatory absenteeism rationale), insulating the judgment from Question 1; (3) the Civil Service Board had already reduced her termination to a 45-day suspension; and (4) her *Loudermill* procedural due-process claim discussed later in `petition.txt` had been waived/abandoned in the district court.

## Predicted reasoning (`predicted_reasoning_quality = 0.85`)

The four testable central claims in `claude-baseline/predicted_reasoning.md` were specific and completely borne out by `outcome.json` and `snapshots/2026-11-16.json`:
1. **First-conference clean denial on November 16, 2026 without a response call** (`borne-out`): The petition was denied on November 16, 2026 out of the November 13 conference with no call for a response.
2. **No further distributions / relists** (`borne-out`): `outcome.json` confirms `signals.distribution_count = 1`.
3. **No CVSG** (`borne-out`): `signals.cvsg_date = null`.
4. **No dissent or statement respecting denial** (`borne-out`): `noted_dissent_from_denial = false`, with a bare `"Petition DENIED."` entry on the docket.

The fifth claim—conditional-on-grant focus on Question 1 and equal split between summary reversal and plenary review—is `unresolved` because certiorari was denied, earning neither credit nor penalty. Because every testable commitment was explicit (naming the conference, projected November 16 order-list date, and absence of CFR, relist, CVSG, and separate writings) and held up in full, the document sits solidly above `0.75`, while remaining below `1.0` because clean first-conference denial of a waived-response pro se baseline petition was the strong consensus expectation from the pre-decision posture rather than a call a competent reader could plausibly have made otherwise.

## Leakage and Big-Case Notes

- **Leakage (`not_applicable`, `leakage_suspected = false`):** Forward prediction executed on `2026-10-31`, sixteen days before the `2026-11-16` denial order. All 11 logged tool calls (`result_capture_coverage = 1.0`) were local reads of provisioned files, schemas, `statpack.md`, and general denied corpus rows, with no exposure to other forecasts.
- **Big-case read (`0.03`):** Routine pro se municipal employment summary-judgment dispute from an unpublished two-sentence Rule 47.6 affirmance with no split, no amici, a waived response, and immediate denial without dissent.
