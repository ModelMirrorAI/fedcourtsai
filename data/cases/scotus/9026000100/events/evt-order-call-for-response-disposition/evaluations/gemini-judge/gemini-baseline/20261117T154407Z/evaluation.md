# Evaluation of `gemini-baseline` — `scotus/9026000100` (`evt-order-call-for-response-disposition`)

## Summary of quantitative scoring

- **Stage:** `cert` (`moment: response-requested`, opened `2026-08-13`, resolved `2026-11-16`). No semantic claim set (`semantic-v1`) or vote accuracy is scored on a cert-stage cell.
- **Outcome match (`correct = 1`):** `gemini-baseline` predicted `denied` (`probability = 0.045`, `granted = 0`), matching `outcome.json` (`actual_disposition = "denied"`, `actual_granted = 0`).
- **Brier score (`0.002025`):** `(0.045 - 0)^2 = 0.002025` — the sharpest calibration in the cohort.
- **Baseline and skill:** Left null for the harness (`segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are computed and stamped by `stamp-cell` from the stamped segment base rate). To check `gemini-baseline`'s base-rate citations against the pack in force when it ran (`run_id = 20261029T160941Z`), we rebuilt that statpack via `fedcourts statpack-at` (`7bcde3b105cb212283905eda17b827efc188e80c`, `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, landed `2026-10-28T13:56:30-04:00`). All `sal-v4` `baseline [reached]`, `elevated`, `ca9`, and amicus figures cited in `reasoning.md` match build `7bcde3b105cb` accurately.

## Reasoning quality (`reasoning_quality = 0.93`)

`gemini-baseline`'s `reasoning.md` is an exemplary piece of Supreme Court cert-stage vehicle analysis:

1. **Complete mastery of the lower-court appendices:** Working solely from the August 13, 2026 petition and appendices (before the October 14 Brief in Opposition was in its information set), `gemini-baseline` read all 2,613 lines of `petition.txt` and anticipated **every major vehicle and record argument** that Respondent's Brief in Opposition subsequently used to defeat review:
   - The investigating police report finding Cross 100% at fault under Cal. Veh. Code § 21760(b) and Cross's own signed statement admitting she was "at complete fault" (App. 6a, 18a, 43a ¶ 69; cf. BIO 6, 13, 22);
   - The post-*Skelly*-hearing on-board video showing no distraction alarm and instead capturing 30 stop-sign/red-light violations, cell-phone use in revenue service, and crosswalk violations (App. 6a, 12a, 21a–22a; cf. BIO 6–7, 13, 22);
   - The decisive structural point that CCCTA **conceded** the *McDonnell Douglas* prima facie case on Cross's retaliation claim (App. 21a) and still won summary judgment at step three under the honest-belief rule (*Villiarimo*), proving that even abolishing or skipping *McDonnell Douglas* step one (as Judge Kavanaugh urged in *Brady*) could not save Cross's claims under ordinary Rule 56 review (cf. BIO 13, 20–23);
   - Comparator dissimilarities (Brown's 25-year tenure and police non-fault determination) plus declaration evidence that at least one driver retained under a last-chance agreement was himself a practicing Muslim (App. 19a; cf. BIO 12–13); and
   - Fatal non-preservation of Section IV's *Abercrombie* accommodation theory because Cross never pleaded failure to accommodate in her complaint (App. 20a n.2; cf. BIO 10).
2. **Sharp institutional comparison to *Hittle* and *Ames*:** `gemini-baseline` cogently explained why a chamber interested in *McDonnell Douglas* (likely Thomas or Gorsuch) would call for a response after Respondent's July 24 waiver, while explaining why a petition far weaker than *Hittle* (`24-427` — published Ninth Circuit opinion, 10 amicus briefs, 5 distributions, still denied with only two noted dissents) warranted discounting *below* the unconditional post-CFR rate down to `0.045`.
3. **Minor imperfection:** `gemini-baseline` treated the zero cert-stage amicus count as of August 13 (eight days before the initial August 21 response due date) as an independent downward factor without noting that amicus briefs commonly arrive on the extended post-CFR schedule (four amicus briefs arrived on September 14, 2026). Even after four amici weighed in, however, the exact factual and preservation obstacles `gemini-baseline` catalogued drove a single-conference, unremarked denial.

## Predicted reasoning (`predicted_reasoning_quality = 0.90`)

`gemini-baseline`'s `predicted_reasoning.md` made highly specific, discriminating commitments across the procedural and substantive dimensions of the cert order, and every testable claim was borne out:

1. **Exact terminal distribution count and conference path (`borne-out`):** Rather than hedging broadly or predicting a *Hittle*-style multi-relist sequence, `gemini-baseline` specifically forecast **one further distribution** (bringing `distribution_count` to `2`) for a fall conference after response briefing, with denial at that conference **without a post-BIO relist**. That matched the realized docket (`2026-10-28` distribution for the `2026-11-13` conference, `distribution_count = 2`, denied `2026-11-16`).
2. **No CVSG (`borne-out`):** Correctly forecast no Solicitor General invitation (`cvsg_date: null`), citing both the local-transit-authority posture and the SG's recent merits participation in *Ames*.
3. **Standard denial after the BIO exposes six record/preservation defects (`borne-out`):** Certiorari was denied (`actual_disposition = "denied"`, `disposition_basis = "standard"`) immediately after Respondent's October 14 BIO laid out the exact six factual, comparator, honest-belief, and pleading obstacles itemized in Section 2 of `predicted_reasoning.md`.
4. **Conditional plenary-over-summary route and narrowed Rule 56 question (`unresolved`):** Untested because certiorari was denied; neither credited nor penalized.
5. **Denial without separate writing (`borne-out`):** Committed strongly (`88%`) to an unannotated denial once the BIO exposed the vehicle's factual and preservation flaws, matching `noted_dissent_from_denial: false`.

Calling `distribution_count = 2` with zero post-BIO relists and zero dissents on a CFR petition squarely targeting Justice Thomas's *Hittle*/*Ames* invitation—and grounding that call in the exact record facts the BIO later marshaled—is discriminating forecasting near the top of the rubric (`0.90`), held just below `1.0` only because an unexplained cert-denial order leaves the Court's internal conference reasoning unobservable and the conditional grant sections untested.

## Leakage and big-case notes

- **Leakage (`not_applicable`, `leakage_suspected = false`):** `gemini-baseline` ran in `forward` mode on `2026-10-29`, eighteen days before the `2026-11-16` resolution. Audit of `retrieval_log.json` (50 calls, `outcome_only` engine capture shape) confirms all queries targeted provisioned `2026-08-13` case files, committed schemas/statpack, and pre-2026 corpus priors (`Hittle`, `Ames`, panel judges), with zero web searches and no `data/qp-topics/` access.
- **Big-case read (`evaluator_score = 0.22`):** While the Question Presented pitched a broad challenge to *McDonnell Douglas* at summary judgment and drew four cert-stage amicus briefs, the case itself was an unpublished single-employee termination dispute resolved by a routine, unremarked cert denial.
