# Evaluation of `claude-baseline` — *Custodia Bank, Inc. v. Federal Reserve Board of Governors, et al.* (`scotus/9026000062`, `evt-petition-disposition`)

## Outcome and Quantitative Summary

- **Stage:** `cert` (`moment: distribution`)
- **Realized outcome:** `denied` (`actual_granted = 0`, `resolved_at = 2026-11-16`, `distribution_count = 1`, `cvsg_date = null`, `noted_dissent_from_denial = false`)
- **Prediction:** `predicted_disposition = denied`, `probability = 0.08`
- **Accuracy & Brier:** `correct = 1`, `brier_score = 0.0064`. On a cert cell, the segment base rate, Brier skill score, base-rate basis record, and mechanical `claim_scores` block are computed and stamped by the harness rather than written by the evaluator.

## Reasoning Quality (`reasoning_quality = 0.85`)

`claude-baseline` delivered a concise, well-calibrated, and factually accurate rationale in `reasoning.md`.

- **Base-rate discipline:** Base-rate references were checked against statpack build `dedb32b153e6` (`sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`), reconstructed via `fedcourts statpack-at` as the build in force for run `20261102T130502Z` (rather than the newer `sal-v8` committed statpack). `claude-baseline` properly anchored on the frozen `baseline` risk-set rate from `context.json` (corresponding to the stamped segment base rate) and used the `2+` cert-amicus bucket only directionally after noting that the marginal split is heavily confounded with relists and CVSGs.
- **Accurate reading of the docket and filings:** `claude-baseline` accurately extracted every procedural fact from the `2026-11-02.json` snapshot: a paid Tenth Circuit petition distributed once for the November 13, 2026 conference, two Briefs in Opposition filed October 13, 2026 (Solicitor General Sauer for the Board of Governors and counsel for FRBKC), three cert-stage amicus briefs (Blockchain Association, The Digital Chamber, and Sen. Lummis with former Sen. Toomey), and an empty `same-question.json`.
- **Sound weighing of cert-stage drivers:** Upward factors (elite petitioner counsel, three amicus briefs including a sitting Senator, and Judge Tymkovich's panel and rehearing dissents on an agency-power statutory issue) were weighed realistically against stronger downward factors that explained the clean first-conference denial: the conceded absence of a circuit split (with the Second Circuit's *Banco San Juan* aligned with the Tenth Circuit and the Ninth Circuit's *PayServices* held in abeyance), active opposition by the Solicitor General despite Executive Order 14,405, vehicle and percolation headwinds from the Board's May 2026 proposed rulemaking on "Payment Accounts" (91 Fed. Reg. 30,627), waiver below of the Appointments Clause theories (alongside *Trump v. Cook*), and Custodia's all-or-nothing statutory entitlement posture.
- **Limitation:** As `claude-baseline` candidly disclosed in its uncertainty section, it did not read the Tenth Circuit opinions in `appendix.txt` directly, relying instead on excerpts quoted in the cert briefs. While that cost some direct engagement with the panel's statutory structure analysis (e.g., 12 U.S.C. § 342 and the Toomey Amendment, § 248c), the analysis was grounded, disciplined, and free of factual error.

## Predicted reasoning

**Grade: `predicted_reasoning_quality = 0.68`.**

`claude-baseline`'s `predicted_reasoning.md` led with five claims: (1) denial of certiorari at the November 13, 2026 conference or after at most one relist; (2) probably no further relists beyond the first distribution (~22% chance); (3) no CVSG because the federal government is already a respondent represented by the Solicitor General; (4) conditional on a grant, review of the statutory QP as written via plenary briefing rather than the waived Appointments Clause issue or a summary GVR; and (5) probably no separate writing or dissent from denial (naming Gorsuch first and Thomas second if one occurred).

Every testable claim—denial, zero additional relists, absence of a CVSG, and absence of a noted dissent from denial—was borne out by the November 16, 2026 order (`actual_disposition = denied`, `distribution_count = 1`, `cvsg_date = null`, `noted_dissent_from_denial = false`), while the conditional-on-grant scope and route claims remained `unresolved` and neither helped nor hurt the grade. The document sits comfortably above the `0.50` generic anchor because it committed cleanly to the right procedural trajectory without error, but below `0.75` because its key propositions were moderately hedged ("most likely", "either at that conference or after at most one relist", "Probably none") and a bare cert denial order on a splitless, SG-opposed docket offers limited discriminating surface (with no-CVSG largely entailed by the federal respondent caption).

## Leakage and Stakes

- **Leakage (`leakage_suspected = false`, `influenced_prediction = not_applicable`):** This was a genuine `forward` prediction completed on November 2, 2026, two weeks before the November 16, 2026 denial order. All 21 tool calls in `retrieval_log.json` were `captured` (`result_capture_coverage = 1.0`) and consisted solely of local workspace reads and two broad corpus queries (`--era roberts` usage error; `--disposition granted --era 2020s --limit 5`), with no web searches, no CourtListener calls, and no `data/qp-topics/` reads.
- **Big-case read (`evaluator_score = 0.42`):** Independent of the candidates' scores, this case carries moderate significance (`0.42`): Reserve Bank master-account gatekeeping matters to state-chartered fintech/crypto depository institutions and dual-banking federalism, attracting top Supreme Court counsel and three amicus briefs, but the narrow splitless statutory posture, waived constitutional claims, pending Fed rulemaking, and clean first-conference denial keep it below high-salience cert or merits blockbusters.
