# Evaluation of `codex-baseline` — *Felicia Scroggins v. City of Shreveport, Louisiana* (`scotus/9026000383`, `evt-petition-disposition`)

## Outcome and Quantitative Summary

- **Stage / Moment:** `cert` / `distribution`
- **Outcome:** Certiorari `denied` on `2026-11-16` (`actual_granted = 0`, `distribution_count = 1`, `cvsg_date = null`, `noted_dissent_from_denial = false`).
- **Prediction:** `predicted_disposition = "denied"`, `probability = 0.007` (`correct = 1`, `brier_score = 0.000049`). The stamped segment base rate and Brier skill score are computed by the harness over the prediction's frozen `baseline` band (`risk_set`).

## Assessment of `reasoning.md` (`reasoning_quality = 0.91`)

`codex-baseline` produced a thorough, closely grounded legal and empirical analysis that engaged the full provisioned record (`petition.txt` and `appendix.txt`), verified key precedent via CourtListener, and handled the `sal-v4` statpack tables carefully.

**What worked well:**
- **Deep lower-court and vehicle analysis:** Unlike a surface read of the questions presented, `codex-baseline` examined the entire Western District of Louisiana summary-judgment ruling in `appendix.txt` and surfaced the concrete factual and doctrinal barriers to certiorari:
  1. Petitioner's absence for 1,153 of 1,779 shifts (64.6% over five years), the 90-day cap on temporary light duty, the psychological fitness-for-duty findings, and her own pre-disciplinary statements that she was not ready to resume full duties.
  2. The district court's **independent alternative pretext holding** (App-17 to App-18 n.1—that the City investigated seven employees above a 20% absenteeism threshold and Petitioner offered no evidence of pretext), which prevented Question 1 from being outcome-determinative.
  3. The Civil Service Board's modification of termination to a 45-day suspension and the district court's holding that Petitioner abandoned her *Loudermill* due-process claim at summary judgment (App-21).
- **Precedent verification:** Used CourtListener MCP to inspect *Tolan v. Cotton*, 572 U.S. 650 (2014), including Justice Alito's concurrence regarding Rule 10 error correction, giving a concrete doctrinal basis for discounting Question 2's summary-vacatur pitch.
- **Statpack and corpus rigor:** Checked against the `sal-v4` statpack build in force at prediction time (`sha256:063aea1961d5833e02e3aa0254477260a34f98f23a2751a1620aaf7c8db03726`, commit `1913c7a1172a` prior to the `sal-v8` rebuild), every rate and denominator `codex-baseline` cited matches the `sal-v4` tables, and `codex-baseline` rightly declined to treat non-comparable interim applications from a general corpus query as cert priors.

**Minor limitations:**
- Did not query the corpus for Petitioner's prior related petition listed on page iii of `petition.txt` (`No. 26-80`, denied October 5, 2026 in the identical waived-response single-distribution posture).
- Setting `P(grant) = 0.007` (more than half of the terminal `baseline` grant+GVR rate across all paid baseline petitions, which mostly comprise represented filings and many petitions with briefs in opposition) was slightly conservative given the combination of pro se status, waived response without a call for response, unpublished Rule 47.6 order, and an independent alternative pretext holding, though still well below the stamped segment base rate.

## Predicted reasoning (`predicted_reasoning_quality = 0.83`)

`codex-baseline/predicted_reasoning.md` committed to four testable propositions on the cert disposition and procedural path, all four of which were borne out by `outcome.json` and `snapshots/2026-11-16.json`:
1. **Denial without explanatory opinion following the November 13, 2026 conference** (`borne-out`): Denied November 16, 2026 by bare order.
2. **No further distribution before disposition** (`borne-out`): `signals.distribution_count = 1`.
3. **No CVSG** (`borne-out`): `signals.cvsg_date = null`.
4. **No dissent or statement respecting denial from any Justice** (`borne-out`): `noted_dissent_from_denial = false`, `votes = []`, `writing_roles = null`.

Its fifth commitment—conditional-on-grant narrowing to Question 2's Rule 56 treatment of Question 1's evidence via a summary disposition—is `unresolved` given the denial, earning neither credit nor penalty. All testable central claims held, placing the forecast comfortably above `0.75`; it sits slightly below `1.0` (and a hair below peers that explicitly projected the November 16 order-list date and no-CFR dead-list mechanics) because first-conference bare denial of a waived-response pro se petition was strongly telegraphed by the pre-decision docket.

## Leakage and Big-Case Notes

- **Leakage (`not_applicable`, `leakage_suspected = false`):** Forward prediction executed on `2026-10-31`, sixteen days before the `2026-11-16` resolution. `retrieval_log.json` (32 calls, `result_capture_coverage = 0.9375`) contains local reads of provisioned files, `statpack.md`, and corpus priors, two CourtListener lookups on *Tolan v. Cotton* (2014), and two unobserved general web queries regarding Supreme Court Rule 10, with zero exposure to case outcome or other predictors' forecasts.
- **Big-case read (`0.03`):** Routine pro se municipal employment summary-judgment dispute from an unpublished two-sentence Rule 47.6 affirmance with no split, no amici, a waived response, and immediate denial without dissent.
