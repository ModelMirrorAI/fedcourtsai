# Evaluation of `codex-baseline` — *Robinhood Markets, Inc. v. Sodha* (`scotus/73280982`, `evt-petition-disposition`)

## Quantitative Summary

- **Stage:** `cert` (`evt-petition-disposition`, resolved `2026-11-13`)
- **Outcome:** `actual_disposition = "granted"`, `actual_granted = 1`, `disposition_route = "plenary"`
- **Prediction:** `predicted_disposition = "granted-in-part"`, `probability = 0.82`
- **Exact-match accuracy (`correct`):** `0` (`"granted-in-part"` against `"granted"`)
- **Brier score (`brier_score`):** `(0.82 - 1)^2 = 0.0324`
- **Baseline & skill:** `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left null for harness stamping against the stamped segment base rate.

## Reasoning Quality (`reasoning_quality = 0.83`)

`codex-baseline` produced a rigorous, well-researched rationale in `reasoning.md` and achieved the sharpest binary calibration on the cell (`probability = 0.82`, `brier_score = 0.0324`), docked primarily for mis-mapping a limited cert grant onto `"granted-in-part"`:

1. **Base-rate grounding (`statpack-at` check):** Verified via `fedcourts statpack-at` against build `eb6830084a18` (`sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`), the statpack build in force at `20261026T092709Z` (`sal-v4`), every figure `codex-baseline` cited—the strictly-prior OT2017–OT2024 `sal-v4` `high`-band figures, unconditional paid CVSG rates, `relist_bucket = 1` rates, and Ninth Circuit originating-court figures—matches build `eb6830084a18`. `codex-baseline` properly distinguished the unconditional CVSG table (which pools SG deny and grant recommendations) from a post-CVSG case carrying an affirmative SG grant recommendation, justifying a crisp upward update over the stamped segment base rate.
2. **Doctrinal and vehicle analysis:** After identifying that `questions-presented.txt` held a body subsection from pages 31–33 at prediction time, `codex-baseline` read `petition.txt`, `sg-invited-brief.txt`, `brief-in-opposition.txt`, and `cert-reply.txt` directly, and verified *Macquarie Infrastructure Corp. v. Moab Partners, L.P.*, 601 U.S. 257 (2024). Its analysis of why Section 11(a)'s misleading-omissions prong cannot collapse misleadingness into materiality under *Omnicare* and *Macquarie*, why the First/Second Circuit tension (*Steckman*, *Shaw*, *Stadnick*) was genuine on Question 1 while Question 2's Item 303 theory lacked a clean split, and why Respondents' alternative-ground vehicle objection failed (because the district court had dismissed both theories and vacatur on Question 1 would reshape the surviving claims on remand) was clear, specific, and accurate.
3. **Cert disposition vocabulary error (`granted-in-part` vs. `granted`):** `codex-baseline` chose `predicted_disposition = "granted-in-part"` because "the United States specifically recommends denying the second question." However, in the pipeline's SCOTUS cert vocabulary (reflected in `statpack.md`'s modern discretionary-cert disposition table, where `granted` has 662 cases and `granted-in-part` has 0), certiorari grants limited to one question presented resolve as `"granted"` (`disposition_route = "plenary"`). That schema/vocabulary error cost `codex-baseline` exact-match accuracy (`correct = 0`) despite its strong substantive analysis and superior Brier score.

## Predicted reasoning (`predicted_reasoning_quality = 0.92`)

Graded strictly on `predicted_reasoning.md` against the staged record, `codex-baseline` wrote the most direct and specific forecast document in the cell, and every testable cert-stage commitment held:

- **Plenary grant limited to reformulated Question 1 and excluding Question 2 (`borne-out`):** `predicted_reasoning.md` opened unconditionally: *"The Court will grant certiorari limited to the first question, reformulated along the lines proposed by the United States: whether materiality of omitted interim financial information suffices under Section 11(a)'s misleading-omissions prong without a separate inquiry into whether the omission rendered an affirmative statement misleading. The second question, concerning Item 303 ... will not be granted."* It also squarely committed to plenary briefing and argument rather than a GVR or summary reversal. On November 13, 2026, the Court entered a plenary grant adopting the Solicitor General's reformulated Question 1 verbatim and leaving Question 2 ungranted.
- **Additional distribution before grant (`borne-out`):** Forecast that the case was likely to receive at least one additional distribution beyond the two recorded at snapshot time as the Court processed the post-CVSG filings and checked the limited-grant formulation after the November 6, 2026 conference, with no further CVSG. The docket records a third distribution on `Nov 09 2026` for the `11/13/2026` Conference (`outcome.signals.distribution_count = 3`) before the `Nov 13 2026` grant.
- **Ordinary unsigned order-list grant without separate writings (`borne-out`):** Correctly forecast an unsigned order-list grant with no separate opinions or noted votes at the cert stage.
- **Expected merits ground (`unresolved`):** Its downstream merits forecast (vacatur and remand under *Omnicare* and *Macquarie* without creating a blanket interim-data exemption or disposing of Item 303) was not tested at the cert stage and neither adds to nor subtracts from the grade.

Because the opening scope and route calls were unhedged, discriminating, and borne out verbatim—with only slight probability hedging on the relist sentence—`predicted_reasoning.md` earns `0.92`.

## Leakage & Retrieval Audit

- **Mode:** `forward` (`leakage_suspected = false`, `influenced_prediction = "not_applicable"`, `retrieved_outcome_material = false`).
- All calls in `retrieval_log.json` (`result_capture_coverage = 0.9302`) ran between `2026-10-26T09:33:07Z` and `2026-10-26T09:40:54Z`, eighteen days before the `2026-11-13` grant order while the petition was genuinely open. Its `find data -name AGENTS.md ... -not -path 'data/qp-topics/*'` call pruned `data/qp-topics/` without opening any file there, and its three `unobserved` web-search calls queried only the 2024 Supreme Court opinion in *Macquarie Infrastructure Corp. v. Moab Partners, L.P.*, 601 U.S. 257 (2024), as transparently logged in `retrieval.md`.

## Big-Case Stake Read (`evaluator_score = 0.60`)

Independently assessed from the case record and granted question, *Robinhood Markets v. Sodha* warrants `0.60`: clarifying whether materiality alone triggers strict Section 11(a) omission liability for intra-quarter financial metrics affects IPO registration statements and securities class actions nationwide (drawing SG/SEC, Chamber of Commerce, and SIFMA participation), while remaining a focused statutory capital-markets dispute rather than a constitutional or administrative-law blockbuster.
