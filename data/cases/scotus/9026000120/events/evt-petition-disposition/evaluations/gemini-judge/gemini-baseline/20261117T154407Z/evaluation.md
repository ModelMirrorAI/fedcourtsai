# Evaluation of `gemini-baseline` — `scotus/9026000120` (`evt-petition-disposition`)

## Outcome and Quantitative Summary

On November 16, 2026, the Supreme Court denied certiorari in *Gays Against Groomers, et al. v. Garcia, et al.* (No. 26-120) directly off the November 13, 2026 conference without any further relist (`distribution_count = 2`), CVSG (`cvsg_date = null`), or noted dissent (`noted_dissent_from_denial = false`).

- **Stage:** `cert` (`moment: distribution`). Baseline and skill fields (`segment_base_rate`, `brier_skill_score`, `base_rate_basis`) are left null for the harness to stamp from the committed statpack.
- **Disposition accuracy (`correct`):** `1` (`denied` vs. `denied`).
- **Probability / Brier (`brier_score`):** `P(grant) = 0.10` → `(0.10 - 0)^2 = 0.01`.
- **Statpack build verified against:** `ca0c9e1a49e292692bdc5b092cd9f868561169b8` (`sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`), reconstructed via `fedcourts statpack-at`. Every statpack count, Tenth Circuit cut, and `amicus-line.json` figure `gemini-baseline` quoted matches that pinned build exactly.

## Reasoning Quality (`reasoning.md` — `0.93`)

`gemini-baseline` delivered the strongest, best-calibrated analysis across both the empirical base-rate structure and the substantive record:

- **Complete, accurate reading of the record below:** `gemini-baseline` read the full Tenth Circuit decision (accurately attributing Judge Federico's majority opinion and Judge Carson's partial concurrence) as well as the Petition, Brief in Opposition, and Reply without factual or procedural missteps.
- **Sharp doctrinal and vehicle synthesis:** `gemini-baseline` nailed all four structural obstacles to certiorari: (1) *Supreme Court of Virginia v. Consumers Union of the United States, Inc.*, 446 U.S. 719 (1980), squarely extends common-law state legislative immunity to § 1983 declaratory and injunctive actions, and every federal circuit addressing state legislators agrees; (2) Petitioners' asserted Fifth and Ninth Circuit conflict (`Minton`, `Schmidt` n.10, and the unpublished `Bols` memorandum) arises exclusively in municipal/county suits lacking Eleventh Amendment sovereign immunity or in brief dicta; (3) Petitioners sued only five state legislators and named no non-legislator enforcement officer such as a sergeant-at-arms (*Powell v. McCormack*; *Kilbourn v. Thompson*), creating a clean vehicle impediment to testing official-capacity prospective relief; and (4) Question 2's First Amendment viewpoint-discrimination challenge is insulated behind Question 1's threshold immunity bar and *Eastland* / *Bogan* / *Houston Community College System v. Wilson*.
- **Disciplined empirical calibration:** Starting from the pinned statpack (`ca0c9e1a49e2`) and cross-checking `amicus-line.json` (`14.7%` at `k = 4`), `gemini-baseline` clearly explained why a petition reaching the `elevated` band solely through four ideological amici and a November 5 pre-conference `Rescheduled` entry warrants a steep discount below the stamped segment base rate—while retaining a calibrated `0.10` tail for First Amendment/viewpoint salience and Judge Carson's concurrence. The only minor quibble in `reasoning.md` is that its `big_case_score` rationale (`0.55`) slightly overstates the national stakes of a narrow state-committee decorum vehicle.

## Predicted reasoning (`predicted_reasoning.md` — `0.85`)

`gemini-baseline`'s forecast document was specific, discriminating, confident, and borne out on every testable dimension:

1. **Immediate conference resolution and exact order-list timing (`borne-out`):** Committed at 75% confidence to resolving the petition directly off the November 13, 2026 conference with no post-conference relist (`distribution_count` remaining 2) and issuing a denial on the **November 16, 2026** order list—matching `outcome.json` (`distribution_count = 2`, `resolved_at = "2026-11-16"`) to the day.
2. **No CVSG (`borne-out`):** Assigned ~1% to a CVSG with clear institutional reasoning why the United States has no federal stake in internal state legislative committee decorum (`cvsg_date = null`).
3. **Disposition (`borne-out`):** Forecast a routine `denied` disposition (90%) with negligible prospect of a GVR or summary reversal (`actual_disposition = "denied"`, `disposition_route = null`).
4. **Routine unwritten denial order (`borne-out`):** Committed strongly (88% conditional on denial, noticeably sharper than a 70/30 hedge) to a routine denial order without a separate writing, explaining specifically why *Consumers Union* and the absence of non-legislator defendants made this an unattractive vehicle even for Justices Thomas, Alito, or Gorsuch to write separately (`noted_dissent_from_denial = false`).
5. **Conditional grant scope (`unresolved`):** Forecast plenary review of both Questions Presented conditional on a grant, which was left untested by the denial.

Within the observable surface of an unreasoned certiorari denial, every central claim `gemini-baseline` made was specific, non-trivial (particularly calling immediate resolution without a relist or separate dissent despite four amici and a prior reschedule), and completely borne out.

## Leakage Assessment

`gemini-baseline` ran in `forward` mode on November 10, 2026 (`20261110T141746Z`), three days before the November 13 conference and six days before the November 16 denial. Although all 24 calls in `retrieval_log.json` carry `result_capture = "unobserved"` (`result_capture_coverage = 0.0`, an engine-level telemetry shape), grading every call on its logged query confirms they consisted solely of local file/directory reads inside the allowed case, schema, and statpack paths, one 2020s corpus query, and local JSON validation, with no web or CourtListener queries (`retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`).
