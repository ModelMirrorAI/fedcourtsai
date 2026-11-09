# Reasoning: *Raul Rivera-Perez v. Caryn Flowers, Warden* (No. 26-396)

- **Case ID:** `scotus/9026000396`
- **Event ID:** `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`)
- **Snapshot:** `2026-10-13.json`
- **Forecast:** `granted: 0`, `probability: 0.42`, `predicted_disposition: "denied"`, `big_case_score: 0.35`

---

## 1. Base-Rate Anchor and Trajectory Position

Under `record/context.json`, this cell is a forward-mode certiorari disposition forecast at the `response-requested` moment (cutoff `2026-10-14`, snapshot `2026-10-13`).

- **Salience Band (`sal-v8`):** `baseline`
- **Registered Anchor (`context.json` `cert_anchor.rate`):** `0.051588` (**5.16%**), which pools the bracketed `[reached]` risk-set grant-family rate for `baseline` petitions across the 10 lookback Terms (`OT2016`–`OT2025`, or as rendered in `metrics/statpack.md` for `OT2017`–`OT2025`, where the reached risk-set rate for private petitions starting in `baseline` ranges from 4.0% to 6.0%).
- **Originating Circuit Base Rate (`metrics/statpack.md`):** Paid discretionary-cert petitions from the Second Circuit (`ca2`, `n = 281`) resolve at 92.6% denied, 2.6% granted, 2.4% GVR, and 2.5% dismissed (5.0% grant-family rate).
- **Relist, CVSG, and Amicus Cuts (`metrics/statpack.md`, paid scored segment):**
  - By relist count: `0` relists (`n = 2667`) grant at 0.3% (0.1% granted, 0.2% GVR); `1` relist (`n = 516`) grants at 19.2% (15.1% granted, 4.1% GVR); `2` relists (`n = 152`) grant at 32.8% (25.1% granted, 7.7% GVR).
  - By CVSG status: `no CVSG` (`n = 3350`) grants at 3.8% (2.6% granted, 1.2% GVR).
  - By amicus-brief count: `0` amici (`n = 365`) grants at 1.9%; `(unknown)` (`n = 2628`) grants at 3.4% (large unknown bucket reflects historical coverage rather than absence of amici).
- **Procedural Posture at Snapshot (`2026-10-13.json`):**
  - Petition filed September 17, 2026 (docketed September 22, 2026, paid docket No. 26-396).
  - The Solicitor General waived the right to respond on September 30, 2026.
  - Distributed on October 7, 2026 (`distribution_count: 1`) for the Conference of November 6, 2026.
  - Before the November 6 Conference, on October 13, 2026, the Court called for a response (`Response Requested. (Due November 12, 2026)`).
  - At the snapshot date, `amicus_briefs` is 0 (`null`), `cvsg_date` is `null`, and the petition has not yet been briefed in opposition, redistributed, or relisted.

Because the Solicitor General routinely waives a response to prisoner/habeas petitions (even represented ones) unless the Court requests one, a Call for a Response (CFR) after a government waiver is a meaningful positive signal that at least one Justice's chambers flagged the petition as potentially certworthy. It filters out the ~80–85% of waived petitions that are summarily denied on the first conference list. However, at the moment the response is merely requested—before the Solicitor General files the Brief in Opposition (BIO) and before the Court considers the petition at conference or relists it—the majority of CFR petitions are still ultimately denied once the government's opposition is received.

---

## 2. Case-Specific Signals and Certworthiness Assessment

### A. Question Presented and Provisioned Filings
We read all provisioned files in `record/documents/` (`questions-presented.txt`, `petition.txt`, and `party-letter.txt`, plus `documents.json`). The petition presents a single question:
> Whether time credits earned under the First Step Act of 2018, Pub. L. No. 115-391, 132 Stat. 5194, can be applied under 18 U.S.C. 3632(d)(4)(C) to reduce a term of supervised release.

Section 3632(d)(4)(C) consists of two sentences:
1. *"Time credits earned under this paragraph by prisoners who successfully participate in recidivism reduction programs or productive activities shall be applied toward time in prerelease custody or supervised release."*
2. *"The Director of the Bureau of Prisons shall transfer eligible prisoners, as determined under section 3624(g), into prerelease custody or supervised release."*

In 2001, Petitioner Raul Rivera-Perez was convicted in D.P.R. of conspiracy to distribute cocaine (21 U.S.C. §§ 846, 841(a)(1)) and sentenced to life imprisonment (later reduced to 360 months) and a mandatory five-year term of supervised release. While incarcerated at FCI Danbury, he accrued 780 days of First Step Act (FSA) time credits. The BOP applied the statutory maximum of 365 days under 18 U.S.C. § 3624(g)(3) to advance the start of his supervised release (releasing him from BOP custody on December 3, 2024), leaving 415 earned credits unused because of a bedspace delay in transferring him to a residential reentry center (RRC).

Judge Underhill (D. Conn.) granted Rivera-Perez's 28 U.S.C. § 2241 habeas petition (`757 F. Supp. 3d 204`), holding that § 3632(d)(4)(C)'s plain text requires applying unused FSA time credits to reduce a term of supervised release. On March 26, 2026, a divided Second Circuit panel (`171 F.4th 196`) vacated and remanded to dismiss the habeas petition as moot (rehearing en banc denied May 20, 2026):
- **Majority (Bianco, J., joined by Jacobs, J.):** Held that "applied toward time in ... supervised release," read in context with the second sentence of § 3632(d)(4)(C) and § 3624(g)(3), means applying credits to accelerate the *start* of supervised release (by up to 12 months), not to reduce the duration of supervised release itself. Judge Jacobs concurred separately.
- **Dissent (Nathan, J.):** Argued that "applied toward time in ... supervised release" unambiguously means reducing the time spent *in* supervised release, and that the majority's reading renders the first sentence of § 3632(d)(4)(C) superfluous alongside § 3624(g)(3) and undermines the FSA's recidivism-reduction incentives.

### B. Strong Upward Adjustments (Why Probability Moves Well Above the 5.16% Anchor)
1. **Acknowledged, Entrenched Circuit Split on Federal Statutory Interpretation:**
   - **Second and Sixth Circuits (plus unpublished 4th, 5th, and 11th Cir. decisions):** Hold that FSA time credits under § 3632(d)(4)(C) cannot reduce a term of supervised release (*Rivera-Perez v. Stover*, 171 F.4th 196 (2d Cir. 2026); *Hargrove v. Healy*, 155 F.4th 530 (6th Cir. 2025)).
   - **Ninth Circuit:** Holds in a published opinion that § 3632(d)(4)(C) unambiguously requires applying excess FSA time credits to reduce a prisoner's term of supervised release (*Gonzalez v. Herrera*, 151 F.4th 1076 (9th Cir. 2025)).
   - The Solicitor General explicitly acknowledged this circuit conflict in its Brief in Opposition in *Hargrove v. Healy*, No. 25-818 (cert. denied Apr. 20, 2026), where the SG opposed cert on the ground that the split was shallow and still percolating (specifically pointing to *Rivera-Perez* pending in the Second Circuit) and that *Hargrove* had a threshold vehicle defect.
2. **Clean Vehicle Curing *Hargrove*'s Threshold Defect:**
   - In *Hargrove v. Healy* (No. 25-818), the petitioner had a disqualifying offense component in his aggregated sentence, so the government argued he was statutorily ineligible to earn FSA credits at all.
   - Here, Rivera-Perez's eligibility to earn and apply FSA time credits is undisputed: the BOP itself awarded him 780 credits and applied 365 of them. Moreover, the statutory question is the sole basis for the Second Circuit's mootness holding, making it strictly outcome-determinative.
3. **Supreme Court's Active Docket on First Step Act Questions & Counsel Quality:**
   - The Court has repeatedly granted certiorari to resolve circuit splits over the First Step Act (*Terry*, *Concepcion*, *Pulsifer*, *Hewitt*, and *Maxwell v. Dinis*, No. 25-5930, granted June 1, 2026, for argument in November 2026).
   - Petitioner is represented by Ashley Robertson of the Federal Public and Community Defenders Supreme Court Project and Michael Qian of Haynes and Boone, LLP, providing sophisticated Supreme Court advocacy in an area typically dominated by *pro se* prisoner filings.
   - The Call for a Response issued on October 13, 2026—just six days after the petition was distributed for the November 6 conference—confirms immediate chamber interest.

### C. Countervailing Downward / Moderating Factors (Why Probability Remains Below 50%)
1. **Lopsided Split and Merits Skepticism:**
   - Every circuit other than the Ninth Circuit to address the question—the Second Circuit (`Rivera-Perez`), Sixth Circuit (`Hargrove`), and panels of the Fourth (`Malik`), Fifth (`Stinson`), and Eleventh (`Guerriero`) Circuits—has agreed with the government that § 3632(d)(4)(C)'s second sentence and cross-reference to § 3624(g)(3) limit the use of FSA time credits to transferring a prisoner into prerelease custody or starting supervised release up to 12 months early.
   - Under the petitioner's and Ninth Circuit's reading, the first sentence of § 3632(d)(4)(C) contains no cap, no recidivism-risk floor (unlike § 3624(g)(1)(D)(ii)'s low/minimum risk requirement), and no implementing mechanism or agency directive for modifying a judicial supervised-release sentence outside 18 U.S.C. § 3583(e). If a majority of Justices view the Second and Sixth Circuits' reading as clearly correct and view the Ninth Circuit as an outlier, they may be less inclined to grant review when the decision below already reached the government-favored result (as reversal is the primary driver of grants, though the Court does sometimes grant to affirm and resolve a split).
2. **Procedural Posture (Pre-BIO, No Amici, No Post-BIO Relist Yet):**
   - At the `response-requested` moment, no Brief in Opposition has yet been filed, no amicus briefs have been filed (`amicus_briefs: null`), and the case has not yet gone through post-BIO conference consideration or relists.
   - Furthermore, the government can still raise potential vehicle or remedial arguments in its forthcoming BIO—for instance, noting that Rivera-Perez was transferred to supervised release in the Middle District of North Carolina (outside the Second Circuit) while the Warden of FCI Danbury is the sole respondent, raising questions about whether a BOP warden can compel an out-of-district U.S. Probation Office (an arm of the judiciary) to shorten a judicial term of supervised release.
   - Finally, the Court is already hearing *Maxwell v. Dinis* (No. 25-5930) in OT2026 regarding § 2241 habeas jurisdiction over FSA time-credit claims, which could interact with the jurisdictional posture of § 2241 petitions seeking FSA credit relief.

---

## 3. Explanation of Secondary Claims and Big-Case Score

- **`disposition` (`0.42`):** Matches top-level `probability: 0.42` (`granted: 0`, `predicted_disposition: "denied"`).
- **`relist-increment` (`0.99`):** At the `response-requested` moment, the petition is guaranteed to be redistributed once the Solicitor General files the Brief in Opposition (or the time to respond expires), which increments `distribution_count` from 1 to at least 2 (note: `relist-increment` is masked by the harness on `response-requested` cells for this reason).
- **`cvsg-increment` (`0.01`):** Because the respondent is a federal prison warden represented by the Solicitor General, the Court will not invite the Solicitor General to file an amicus brief via CVSG.
- **`summary-disposition-route` (`0.05`):** Conditional on a grant, the Court would almost certainly set the case for plenary briefing and oral argument to resolve the published circuit split. There is only a small (~5%) conditional chance of a GVR (e.g., if the decision in *Maxwell v. Dinis*, No. 25-5930, bears on § 2241 jurisdiction).
- **`dissent-from-denial` (`0.08`) & `order-writers`:** Conditional on a denial, there is an ~8% chance that one or more Justices (most likely Justice Jackson, Sotomayor, or Gorsuch) write a dissent or statement respecting the denial to highlight the acknowledged circuit conflict affecting federal inmates nationwide.
- **`big_case_score` (`0.35`):** If decided on the merits, the case would resolve an important and recurring statutory question under the First Step Act affecting thousands of federal prisoners and the administration of supervised release by the BOP and U.S. Probation Offices, though it is a technical statutory interpretation case rather than a constitutional or major separation-of-powers dispute.
