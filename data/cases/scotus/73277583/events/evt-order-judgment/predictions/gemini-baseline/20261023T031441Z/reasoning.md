# Predictor Rationale — *Kendrick Jarrell Beaird v. United States* (`scotus/73277583`, `evt-order-judgment`)

## 1. Headline Numbers

- **`probability` (`P(judgment-disturbed)`):** `0.78` (`granted = 1`, `predicted_disposition = "other"`)
- **`judgment`:** `"vacated"`
- **Implicit judgment distribution:**
  - Disturbed (`0.78` total): `vacated` = `0.60`, `reversed` = `0.17`, `affirmed-in-part-reversed-in-part` = `0.01`
  - Undisturbed (`0.22` total): `affirmed` = `0.19`, `dismissed-as-improvidently-granted` = `0.03`, `affirmed-by-an-equally-divided-court` = `0.00`
- **`big_case_score`:** `0.75`

## 2. Information Set and Provisioned Record

This is a `mode: "forward"` merits cell at `moment: grant` (`event_id: evt-order-judgment`, `opened_at: 2026-04-20`, `cutoff: 2026-04-21`). I worked from the provisioned cert-stage record in `data/cases/scotus/73277583/record/`:
- **Provisioned snapshot:** `2026-04-21.json` (`snapshot_provenance: "truncated"`). The dated `ProceedingsandOrder` entries stop at the April 20, 2026 grant order:
  > *"Motion to proceed in forma pauperis GRANTED. Petition for a writ of certiorari GRANTED limited to the following question: Whether Stinson v. United States, 508 U. S. 36 (1993), still correctly states the rule for the deference that courts must give the commentary to the Sentencing Guidelines."*
  Because the snapshot provenance is `truncated`, the undated top-level `Other` counsel block reflects later docket metadata and already lists Anthony J. Dick (Jones Day) as "Court-appointed amicus curiae" alongside eight amici curiae (National Association of Criminal Defense Lawyers, Cato Institute, National Association of Federal Defenders / Stanford Supreme Court Litigation Clinic, Chamber of Commerce of the United States, FAMM, New Civil Liberties Alliance, The Buckeye Institute, and the State of West Virginia).
- **Provisioned documents (`record/documents/`):** As expected for a `moment: grant` cell bounded by `cutoff: 2026-04-21`, no merits briefs or argument transcript were provisioned in `record/documents/`. I read all four provisioned cert-stage documents listed in `documents.json` (none had `empty_text: true` or `truncated: true`):
  - `questions-presented.txt` (the three cert questions presented by petitioner)
  - `petition.txt` (35 pages, filed August 11, 2025 by the Federal Public Defender for the Northern District of Texas)
  - `brief-in-opposition.txt` (17 pages, filed January 9, 2026 by the Solicitor General)
  - `appendix.txt` (14 pages, containing the Fifth Circuit's unpublished per curiam opinion in *United States v. Beaird*, No. 24-10764, 2025 WL 1410410 (5th Cir. May 15, 2025), and the district court judgment)
- I did not retrieve post-grant merits briefs or oral argument transcripts outside the provisioned baseline.

## 3. Base-Rate Anchor (`metrics/statpack.md`)

Per the merits-stage contract, cert-stage signals (`distribution_count: 7`, `band: "high"`) are spent upon the grant of certiorari and are not used to anchor the merits forecast. Instead, I anchored on **"The merits docket (granted cases)"** section of `metrics/statpack.md`, which publishes an `excluded (not in granted)` column verifying the grant-date pool guard.

- **Grant Term:** Certiorari was granted on April 20, 2026 (`event.opened_at = '2026-04-20'`). Under the October-1 convention, grants before October 1, 2026 belong to **OT2025**.
- **Strictly preceding grant Terms in the statpack (`2015 <= T < 2025`, rendered as OT2017–OT2024):**
  Pooling `disturbed` over `parsed` across the 8 grant Terms strictly preceding OT2025 in `metrics/statpack.md` (OT2017 through OT2024):
  - **OT2024:** 50 disturbed / 73 parsed (68.5%; 75 granted, 34 excluded)
  - **OT2023:** 34 disturbed / 55 parsed (61.8%; 55 granted, 13 excluded)
  - **OT2022:** 50 disturbed / 73 parsed (68.5%; 74 granted, 1 excluded)
  - **OT2021:** 46 disturbed / 65 parsed (70.8%; 67 granted, 1 excluded)
  - **OT2020:** 57 disturbed / 69 parsed (82.6%; 79 granted, 2 excluded)
  - **OT2019:** 42 disturbed / 54 parsed (77.8%; 56 granted, 2 excluded)
  - **OT2018:** 50 disturbed / 75 parsed (66.7%; 77 granted, 0 excluded)
  - **OT2017:** 31 disturbed / 52 parsed (59.6%; 56 granted, 3 excluded)
  - **Pooled prior baseline (OT2017–OT2024):** **360 disturbed / 516 parsed = 69.8%** (covering 516 parsed judgments out of 539 merits-opening grants across those eight Terms, with 56 excluded cert-order dispositions removed by the guard; well above the 30-judgment floor). Within those 516 parsed judgments, the label breakdown is: `reversed` 235 (45.5%), `affirmed` 140 (27.1%), `vacated` 115 (22.3%), `dismissed-as-improvidently-granted` 12 (2.3%), `affirmed-in-part-reversed-in-part` 10 (1.9%), and `affirmed-by-an-equally-divided-court` 4 (0.8%).

## 4. Case-Specific Adjustments from the 69.8% Base Rate

Starting from the **69.8%** pooled base rate for disturbing the judgment below, I adjust upward by **+8.2 percentage points** to **0.78** (`P(disturbed)`), and select **`vacated`** over `reversed` as the modal judgment class, for four concrete reasons grounded in the record:

1. **Both parties reject the Fifth Circuit's *Stinson* rule (+10% toward disturbing the judgment):**
   In the decision below (App. A2), the Fifth Circuit summarily affirmed Beaird's sentence solely because his challenge to `U.S.S.G. § 2K2.1(a)(3)` Application Note 2 was foreclosed by *United States v. Martin*, 119 F.4th 410, 414–15 (5th Cir. 2024), which in turn followed the Fifth Circuit's en banc holding in *United States v. Vargas*, 74 F.4th 673, 683 (5th Cir. 2023), that *Stinson v. United States*, 508 U.S. 36 (1993), remains unmodified by *Kisor v. Wilkie*, 588 U.S. 558 (2019). However, in its Brief in Opposition (at 9–10), the Solicitor General expressly conceded that "*Kisor* sets the standard for determining whether particular Guidelines commentary is entitled to deference" and stated that "[t]o the extent that petitioner argues that *Kisor* now governs the degree of deference owed to an agency's interpretation of its regulations, the government agrees." Because neither Petitioner nor the United States defends unmodified *Stinson*, the Court appointed amicus curiae (Anthony J. Dick) to defend the Fifth Circuit's doctrinal position.
2. **Doctrinal alignment across all nine Justices against unmodified *Stinson* (+4%):**
   In *Kisor*, 588 U.S. at 568 n.3, Justice Kagan's opinion explicitly cited *Stinson* as a decision applying *Seminole Rock*/*Auer* deference and held that such deference applies only when a regulation remains genuinely ambiguous after exhausting all traditional tools of construction. The Justices who did not join that portion of *Kisor* (Roberts, C.J., in part; Gorsuch, Thomas, Alito, and Kavanaugh, JJ., concurring in the judgment) and Justice Barrett (who joined *Loper Bright Enterprises v. Raimondo*, 603 U.S. 369 (2024)) are even more skeptical of binding agency deference. Thus, the likelihood that a majority of the Court upholds the Fifth Circuit's rule that *Stinson* survives untouched by *Kisor* is very low (~8%).
3. **Why the Court's narrowed Question Presented points strongly to `vacated` (0.60) rather than `reversed` (0.17) or alternative-ground `affirmed` (0.19) (-5.8% offset for alternative-ground affirmance risk):**
   In the Brief in Opposition (at I, 12), the Solicitor General attempted to reframe Question 2 around whether the district court correctly determined that a 17-round magazine qualifies as a "large capacity magazine" under `U.S.S.G. § 2K2.1(a)(3)`, arguing that even under *Kisor*, the Third and Ninth Circuits (*United States v. McIntosh*, 124 F.4th 199 (3d Cir. 2024); *United States v. Trumbull*, 114 F.4th 1114 (9th Cir. 2024)) held that "large capacity magazine" is genuinely ambiguous and deferred to Application Note 2's >15-round threshold.
   Critically, the Supreme Court **declined** the Solicitor General's framing and limited the grant strictly to the threshold methodological question: *"Whether Stinson v. United States, 508 U. S. 36 (1993), still correctly states the rule for the deference that courts must give the commentary to the Sentencing Guidelines."* Just as in *Kisor v. Wilkie*, 588 U.S. at 590 — where the Court clarified the deference standard, declined to apply it in the first instance, and vacated and remanded for the court of appeals to apply the proper framework — the overwhelmingly likely disposition here is **vacatur and remand (`vacated`)** so the Fifth Circuit can address `U.S.S.G. § 2K2.1(a)(3)` under the correct standard in the first instance.
4. **Main uncertainties and why `P(disturbed)` is not higher than `0.78`:**
   - **Alternative-ground affirmance (~11%):** The Solicitor General will likely argue on the merits that, after holding *Kisor* governs in place of unmodified *Stinson*, the Court should nevertheless affirm the Fifth Circuit's judgment on the alternative ground that `U.S.S.G. § 2K2.1(a)(3)` is genuinely ambiguous and Application Note 2's 15-round definition is reasonable under *Kisor*. While the Court's deliberate narrowing of the Question Presented cuts strongly against reaching that downstream issue, there remains roughly an 11% chance the Court affirms on that alternative ground.
   - **Endorsement of Court-appointed amicus (~8%):** There is a small (~8%) chance that a majority accepts the Court-appointed amicus's institutional argument that the Sentencing Commission's unique statutory role under 28 U.S.C. § 994 distinguishes Guidelines commentary from executive agency interpretations under *Kisor*, yielding an affirmance (`0.11 + 0.08 = 0.19` total for `affirmed`).
   - **DIG risk (~3%):** There is a modest (~3%) chance of `dismissed-as-improvidently-granted` if the Court concludes after briefing or argument that the overlap between *Kisor* and the third/ninth circuit holdings on Application Note 2 makes this case an imperfect vehicle for deciding whether commentary deference survives at all.
   - **Vacatur vs. outright reversal:** If a majority goes beyond *Kisor* and holds that Sentencing Guidelines commentary receives *no* binding deference (or cannot expand a criminal guideline range), the Court could `reverse` (`0.17`) rather than `vacate` (`0.60`), though even under a no-deference holding the Court commonly vacates and remands for the circuit court to interpret the Guideline text de novo.
