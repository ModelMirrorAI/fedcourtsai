# Evaluation — `claude-baseline` (`scotus/9026000239`, `evt-petition-arrival-disposition`)

## Outcome and Quantitative Summary

- **Stage / moment:** `cert` (`moment: arrival`, opened `2026-08-24`).
- **Outcome (`2026-11-13`):** Certiorari **granted** (`actual_disposition: "granted"`, `actual_granted: 1`, `disposition_route: "plenary"`, `disposition_basis: "standard"`), after two distributions (`11/06/2026` and `11/13/2026`, `distribution_count: 2`) and no CVSG (`cvsg_date: null`), with the docket order reading: *"Petition GRANTED limited to Questions 1 and 2 presented by the petition."*
- **Prediction:** `predicted_disposition: "granted"`, `probability: 0.92` (`correct = 1`, `brier_score = 0.0064`), outperforming the stamped segment base rate.

## Rationale Quality (`reasoning_quality`: 0.91)

`claude-baseline`'s `reasoning.md` is empirically disciplined, institutionally sharp, and well-calibrated to the arrival vantage:

1. **Exact historical base-rate anchoring.** Because the committed `metrics/statpack.md` has since advanced to `sal-v8`, `claude-baseline`'s base-rate figures were checked against the reconstructed statpack build in force at its run (`02dd6a20fccc`, `sha256:5b70d73d2cadac0dff2091d5aa32536fb116a3366f76592493006ca63337d0cc`, `sal-v3`). Every per-Term denominator (`n = 21, 15, 29, 19, 11, 40, 26, 23, 17`, summing to `201` across OT2017–OT2025) and the Term-to-Term range (`43.5%` to `89.5%`) match build `02dd6a20fccc` verbatim. `claude-baseline` also rightly explains why the bracketed risk-set `federal` rate — rather than the terminal zero-relist bucket — is the proper arrival anchor for a newly docketed SG petition with zero distributions.
2. **Institutional and procedural drivers.** Rather than relying solely on "the SG usually wins cert," `claude-baseline` pinpoints the specific features pushing this case far above routine SG error-correction petitions: (a) final invalidation of a flagship presidential border proclamation on par with *Trump v. Hawaii*, *Biden v. Texas*, *DHS v. Regents*, and *Trump v. CASA*; (b) the D.C. Circuit's stay of its own mandate pending certiorari, signaling appellate expectation of Supreme Court review and tying continued operation of the policy to certiorari; (c) the impossibility of further circuit percolation because universal class relief in D.C. forecloses parallel suits; and (d) independent remedial leverage under 8 U.S.C. § 1252(f)(1) (*Garland v. Aleman Gonzalez*).
3. **Downside calibration and arrival asymmetry.** Holding at `0.92` rather than `0.98–0.99` at docketing — before the September 23 BIO or any conference — is thoughtfully justified by decomposing the `~8%` non-grant tail into pre-conference mootness, proclamation rescission/supersession, or vehicle complications rather than an implausible straight merits shrug. Its explanations of the auxiliary claims (`relist-increment` as first-distribution reach from `0`, near-zero `cvsg-increment` with the SG as petitioner, and `0.04` conditional summary route) and arrival-moment record limits (truncated petition appendix, absent BIO) are clear and coherent.
4. **Minor limitation.** Compared with the deepest doctrinal treatment possible from the petition text, `reasoning.md` spends little space on the substantive statutory tension between 8 U.S.C. § 1182(f) and § 1158(a)(1) or the June 2026 *Mullin v. Al Otro Lado* comparator, though for cert-stage institutional analysis that omission is minor.

## Predicted reasoning (`predicted_reasoning_quality`: 0.94)

`claude-baseline`'s `predicted_reasoning.md` was remarkably specific and borne out on every cert-stage commitment resolved by the staged record:

- **Plenary grant and timing (central, borne out):** Forecast a plenary certiorari grant (putting conditional cert-order summary disposition around 4%) in "late 2026 or very early 2027." The Court granted plenary review on November 13, 2026.
- **Opposition, first distribution, relist path, and no CVSG (central, borne out):** Forecast that institutional respondents would oppose rather than waive, placing first distribution in October or November 2026, followed by "one or two relists at most" (a grant within one to three conferences of first distribution) and no CVSG. Respondents filed their BIO on September 23, 2026; the case was first distributed October 7, 2026 for the November 6 conference, relisted once on November 9, 2026, and granted at its second conference on November 13, 2026 (`distribution_count: 2`, `cvsg_date: null`).
- **Question-by-question grant scope (central, borne out):** Specifically differentiated all three questions presented — calling QP 1 certain to be taken, QP 2 (§ 1252(f)(1)) "very likely" to ride along, and QP 3 (Rule 23 / Article III class definition) "the most likely to be pruned or subsumed; the Court could grant limited to QPs 1 and 2." That discriminating call matched the November 13, 2026 order verbatim (*"Petition GRANTED limited to Questions 1 and 2 presented by the petition"*).
- **Post-grant merits and denial branches (conditional, unresolved):** Its projections of OT2026 argument/June 2027 decision and likely merits reversal remain unresolved at the cert-grant snapshot, and its conditional denial discussion was untested. Only mild epistemic hedging ("could grant limited to QPs 1 and 2") keeps the document just shy of 1.0.

## Leakage Assessment

- **Mode:** `forward` (`run_id: 20260824T231410Z`, `result_capture_coverage: 1.0`).
- **Assessment:** Clean (`retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`). The prediction ran on the day the petition was docketed (`2026-08-24`), nearly three months before the `2026-11-13` grant order. All 28 logged tool calls had full result capture, touched only pre-decision filings, prior-Term statpack tables, generic corpus queries, and lower-court CourtListener results predating docketing, and never accessed `data/qp-topics/`.
