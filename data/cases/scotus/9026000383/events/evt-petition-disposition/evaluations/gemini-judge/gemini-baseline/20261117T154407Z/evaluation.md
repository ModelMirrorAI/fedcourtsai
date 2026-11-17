# Evaluation of `gemini-baseline` — *Felicia Scroggins v. City of Shreveport, Louisiana* (`scotus/9026000383`, `evt-petition-disposition`)

## Outcome and Quantitative Summary

- **Stage / Moment:** `cert` / `distribution`
- **Outcome:** Certiorari `denied` on `2026-11-16` (`actual_granted = 0`, `distribution_count = 1`, `cvsg_date = null`, `noted_dissent_from_denial = false`).
- **Prediction:** `predicted_disposition = "denied"`, `probability = 0.002` (`correct = 1`, `brier_score = 0.000004`). The stamped segment base rate and Brier skill score are computed by the harness over the prediction's frozen `baseline` band (`risk_set`).

## Assessment of `reasoning.md` (`reasoning_quality = 0.96`)

`gemini-baseline` delivered the strongest and most comprehensive rationale in the cell, combining exact `sal-v4` base-rate decomposition, complete command of the lower-court summary-judgment record, sharp procedural reasoning on waived-response distributions, and a verified corpus lookup of Petitioner's directly analogous prior petition (`No. 26-80`).

**What worked well:**
- **Exact statpack grounding:** Checked against the `sal-v4` statpack build in force at prediction time (`sha256:063aea1961d5833e02e3aa0254477260a34f98f23a2751a1620aaf7c8db03726`, commit `1913c7a1172a` prior to the `sal-v8` rebuild), every rate and sample count cited by `gemini-baseline` across the `baseline` risk-set, terminal `baseline`, `relist_bucket = 0`, `cert_amicus = 0`, `cvsg = none`, and `ca5` tables reproduces exactly, and `gemini-baseline` cleanly explained why this petition sits far below the stamped segment base rate and even well below the terminal `baseline` average (`P(grant) = 0.002`).
- **Mastery of the lower-court appendix and vehicle defects:** Accurately synthesized all independent barriers in the Western District of Louisiana's ruling (`appendix.txt`): (1) 1,153 missed shifts out of 1,779 workdays (64.6% over five years) and the 90-day temporary light-duty policy cap; (2) the October 17, 2022 fitness-for-duty evaluation and January 19, 2023 Pre-Disciplinary Conference statements confirming Petitioner was not prepared to resume full Fire Engineer duties; (3) the **independent alternative holding** under *McDonnell Douglas* (App-17 to App-18 n.1—no evidence of pretext for the City's investigation of seven employees exceeding 20% absenteeism), which completely insulates the judgment from Question 1; and (4) the Civil Service Board's reduction of termination to a 45-day suspension alongside Petitioner's district-court waiver of her *Loudermill* due-process claim (App-21).
- **Directly probative companion-docket verification:** Noticed `No. 26-80` in the petition's Related Proceedings section and queried `fedcourts query --court scotus --docket-number "26-80"`, confirming (`scotus/9026000080`) that Petitioner's prior pro se petition against the City of Shreveport from her 2018 suit (`CA5 No. 24-30777`) had just been distributed once on September 28, 2026 without a response or relist and denied on October 5, 2026.

## Predicted reasoning (`predicted_reasoning_quality = 0.85`)

All four testable central commitments in `gemini-baseline/predicted_reasoning.md` were specific and completely borne out by `outcome.json` and `snapshots/2026-11-16.json`:
1. **Clean denial out of the November 13, 2026 conference on the November 16, 2026 order list without requesting a response** (`borne-out`): Denied November 16, 2026 with no response requested.
2. **No relist or reschedule past the single October 28 distribution** (`borne-out`): `signals.distribution_count = 1`.
3. **No CVSG** (`borne-out`): `signals.cvsg_date = null`.
4. **No dissent from or statement respecting denial from any Justice** (`borne-out`): `noted_dissent_from_denial = false`, `votes = []`, `writing_roles = null`.

Its fifth point—conditional-on-grant selection of Question 1 over Question 2 and the unpreserved *Loudermill* argument, favoring plenary review (65%) over summary disposition (35%)—is `unresolved` because certiorari was denied, earning neither credit nor penalty. As with `claude-baseline`, explicit, accurate commitments on conference, November 16 order-list date, dead-list/no-CFR posture, zero relists, zero CVSG, and zero separate writings place the forecast solidly above `0.75`, while keeping it below `1.0` because first-conference clean denial was the clear consensus expectation from the pre-decision docket rather than a call a competent reader could plausibly have made otherwise.

## Leakage and Big-Case Notes

- **Leakage (`not_applicable`, `leakage_suspected = false`):** Forward prediction executed on `2026-10-31`, sixteen days before the `2026-11-16` denial order. Tool call parameters in `retrieval_log.json` (35 calls, `outcome_only` capture) confirm reads of provisioned files and `statpack.md`, legitimate forward corpus lookup of already-resolved companion petition `No. 26-80` (denied `2026-10-05`) and 2020s priors, and CourtListener opinion searches for *Weber v. BNSF Railway* and prior Fifth Circuit *Scroggins* rulings, with no forecast exposure.
- **Big-case read (`0.03`):** Routine pro se municipal employment summary-judgment dispute from an unpublished two-sentence Rule 47.6 affirmance with no split, no amici, a waived response, and immediate denial without dissent.
