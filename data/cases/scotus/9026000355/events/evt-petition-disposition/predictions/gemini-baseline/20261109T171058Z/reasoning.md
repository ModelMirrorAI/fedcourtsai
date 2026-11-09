# Predictor Rationale (`scotus/9026000355` — `evt-petition-disposition`)

## 1. Summary of Forecast

- **Binary Prediction:** `granted = 0` (`predicted_disposition = "denied"`)
- **Grant Probability (`probability` / `disposition`):** `0.06` (6.0%)
- **Increment & Conditional Claims:**
  - `relist-increment`: `0.97`
  - `cvsg-increment`: `0.015`
  - `summary-disposition-route`: `0.08`
  - `dissent-from-denial`: `0.02`
- **Big Case Score (`big_case_score`):** `0.55`

## 2. Base-Rate Anchoring (`metrics/statpack.md` and `record/context.json`)

This is a `forward`-mode (`decided_before: null`, `cutoff: null`), `cert`-stage cell at `moment: distribution` for *Julio del Rio, et al. v. CrowdStrike, Incorporated, et al.*, No. 26-355.

1. **Salience Band Risk-Set Anchor (`cert_anchor`):**
   - In `record/context.json`, the harness froze `band: "baseline"`, `salience_version: "sal-v8"`, `distribution_count: 1`, `cvsg_date: null`, `amicus_briefs: null`, and `term: 2026`.
   - The pooled 10-term lookback risk-set base rate in `context.json` (`cert_anchor.rate`) is **`0.051587928582714486` (~5.16%)** across OT2016–OT2025.
   - In `metrics/statpack.md` ("Segment base rate by salience band (sal-v8)"), the prior-Term rows rendered for `baseline` show the following `[reached]` risk-set rates (and terminal rates):
     - OT2025: `1.3% (n=1116) [reached 4.0%, n=1290]`
     - OT2024: `1.5% (n=1030) [reached 6.0%, n=1243]`
     - OT2023: `1.9% (n=1048) [reached 6.0%, n=1283]`
     - OT2022: `1.5% (n=981) [reached 5.9%, n=1183]`
     - OT2021: `1.5% (n=1239) [reached 5.7%, n=1469]`
     - OT2020: `1.5% (n=1443) [reached 4.7%, n=1697]`
     - OT2019: `1.9% (n=1163) [reached 4.7%, n=1369]`
     - OT2018: `1.6% (n=1288) [reached 4.8%, n=1509]`
     - OT2017: `0.7% (n=1343) [reached 5.0%, n=1615]`
   - The `baseline` reached rate (~5.16%) represents the unconditional grant-family rate across all private paid petitions entering the `baseline` risk set (including those that later draw a response request, relists, or a CVSG and climb into `elevated` or `high`), whereas petitions that *end* in `baseline` without ever being redistributed have a ~1.5% grant-family rate (`denied 97.3%, dismissed 1.3%, granted 0.8%, gvr 0.6%` over `n=11020` resolved in `statpack.md`).

2. **Cross-Checking Other Statpack Cuts:**
   - **Originating Circuit (`ca5`):** In "Modern cert petitions by originating circuit" (`statpack.md`), Fifth Circuit petitions (`n=5418` resolved) resolve `denied 94.6%, gvr 2.3%, dismissed 1.6%, granted 1.6%` (a 3.9% grant+GVR rate; in the state-inclusive table, `n=4527` resolved: `denied 93.6%, gvr 2.7%, dismissed 1.9%, granted 1.9%`, or 4.6% grant+GVR).
   - **Amicus Count (`0`):** In "Cert petitions by amicus-brief count (paid scored segment)", petitions ending with `0` cert-stage amicus briefs (`n=11109` resolved) resolve `denied 95.0%, granted 2.0%, gvr 1.8%, dismissed 1.3%` (3.8% grant+GVR).
   - **Relist Count (`0` vs. `1`):** In "Cert petitions by relist count (paid scored segment)", `relist_bucket = 0` (`n=10204` resolved) resolves `denied 96.8%, dismissed 1.3%, granted 1.3%, gvr 0.5%` (1.8% grant+GVR), while `relist_bucket = 1` (`n=2532` resolved—which includes petitions redistributed once after a called-for response as well as true one-time post-conference relists) resolves `denied 85.5%, granted 8.3%, gvr 5.2%, dismissed 1.0%` (13.5% grant+GVR).

## 3. Case-Specific Adjustments from the Provisioned Record

### A. Upward Adjustment: Call for a Response After Waiver (`2026-11-09.json`)
The provisioned snapshot (`record/snapshots/2026-11-09.json`) shows that after Respondents CrowdStrike, Inc. and CrowdStrike Holdings, Inc. filed a waiver of the right to respond on October 10, 2026, and the petition was distributed on October 14, 2026 for the November 6, 2026 Conference, the Court issued a **Call for a Response (CFR)** on October 19, 2026 (`Response Requested. (Due November 18, 2026)`).

This procedural signal is important in two ways:
1. It confirms that the petition cleared the initial waiver screen—at least one chambers flagged the petition as warranting adversarial briefing rather than summary denial on the November 6 conference list. That places this petition above the ~1.5% terminal `baseline` rate and modestly above the 5.16% `cert_anchor.rate` before considering vehicle defects.
2. Mechanically, because `context.json` froze `distribution_count: 1` as of the initial October 14 distribution, and the petition will be redistributed for conference after Respondents file their Brief in Opposition (due November 18, 2026), the petition is virtually certain (`relist-increment = 0.97`) to accumulate at least one more distribution entry on the docket unless dismissed under Rule 46 first.

### B. Downward Adjustments: Severe Vehicle and Split Defects (`petition.txt`, `decision-below.txt`, `lower-court-docket.txt`)
Weighing the petition (`record/documents/petition.txt`), the Questions Presented (`record/documents/questions-presented.txt`), the Fifth Circuit's judgment (`record/documents/decision-below.txt`), and the lower-court docket (`record/documents/lower-court-docket.txt`) reveals compelling reasons why the Court is highly likely to deny certiorari once Respondents' Brief in Opposition (by DLA Piper) is filed:

1. **Unpublished One-Word Rule 47.6 Summary Affirmance Below:**
   As confirmed by both `decision-below.txt` and Appendix A of `petition.txt` (App. 1a), the Fifth Circuit panel (Judges Richman, Duncan, and Oldham) disposed of the appeal via an unpublished per curiam order reading in its entirety: `"AFFIRMED. See 5th Cir. R. 47.6."` Rehearing en banc was denied on June 15, 2026 with no judge requesting a poll (App. 16a–17a; `lower-court-docket.txt`). Under Fifth Circuit Rule 47.6, summary affirmances without opinion carry no precedential weight and reflect the panel's view that no error of law appears. The Supreme Court is exceedingly reluctant to grant plenary review on a complex statutory preemption question when the court of appeals wrote no opinion at all—leaving only a single district judge's Rule 12(b)(6) order (`del Rio v. CrowdStrike, Inc.*, No. 1:24-CV-881-RP, W.D. Tex. June 18, 2025, App. 2a–15a) to review.

2. **The *Hodges* / *Charas* Circuit Split on "Service" (Question 1) Is Not Implicated:**
   Petitioners' primary cert argument (Pet. 11–20) invokes the decades-old circuit split over the general definition of "service of an air carrier" in 49 U.S.C. § 41713(b)(1)—contrasting the broader "bargained-for or anticipated provision of labor" definition in *Hodges v. Delta Airlines, Inc.*, 44 F.3d 334, 336 (5th Cir. 1995) (en banc) (followed by the First, Fourth, Seventh, Eighth, Tenth, and Eleventh Circuits), with the narrower "public utility" definition in *Charas v. Trans World Airlines, Inc.*, 160 F.3d 1259, 1261, 1265–66 (9th Cir. 1998) (en banc), and *Taj Mahal Travel, Inc. v. Delta Airlines, Inc.*, 164 F.3d 186, 193–94 (3d Cir. 1998).
   However, that split concerns whether *incidental onboard or terminal occurrences* (such as beverage-cart collisions, overhead bin injuries, or baggage mishandling) constitute airline "services." Even under *Charas*, "service" explicitly encompasses `"the prices, schedules, origins and destinations of the point-to-point transportation of passengers."` 160 F.3d at 1261. Here, as Judge Pitman's opinion details (App. 3a–4a, 7a–8a), Petitioners are airline passengers suing exclusively over **flight delays and cancellations** and the resulting out-of-pocket costs of rebooking flights, lodging, ground transportation, and missed work. Point-to-point flight scheduling and cancellations lie at the core of "service" in *every* circuit, making this case a poor vehicle to resolve the *Hodges*/*Charas* split.

3. **No Circuit Conflict on Third-Party Vendor Preemption (Question 2):**
   On the second question presented—whether § 41713(b)(1) preempts state-law negligence and public-nuisance claims against a third-party software vendor whose defective update grounded flights—Petitioners identify **no** decision from any federal court of appeals or state court of last resort holding that passenger tort claims seeking flight-delay damages from an airline's technology or operational vendor survive ADA preemption. As the District Court noted (App. 9a–12a), Plaintiffs' own Consolidated Complaint alleged that the airlines `"rely heavily on cyber and network support to operate the[ir] essential systems,"` that the Falcon update disrupted airline systems `"used for calculating aircraft weight, checking in customers, and phone systems in [airline] call centers,"` and that passengers `"relied on CrowdStrike's performance of its ongoing services to keep CrowdStrike's airline customers' airplanes flying as scheduled"` (Am. Compl. at 34, 38, 52). Lower courts have consistently applied ADA preemption to non-airline technology/reservation vendors where the claims relate to and would significantly affect airline services (*Lyn-Lea Travel Corp. v. Am. Airlines, Inc.*, 283 F.3d 282, 287 n.8 (5th Cir. 2002); *In re Am. Airlines, Inc., Privacy Litig.*, 370 F. Supp. 2d 552, 564–65 (N.D. Tex. 2005); *Gordon v. Amadeus IT Grp., S.A.*, 194 F. Supp. 3d 236, 246 (S.D.N.Y. 2016); *Pica v. Delta Air Lines, Inc.*, 2019 WL 1598761, at *9 (C.D. Cal. Feb. 14, 2019)).

4. **Absence of Cert-Stage Amici and Companion Petitions:**
   No amicus briefs have been filed in support of the petition (`amicus_briefs: null` in `context.json`), and `record/same-question.json` shows zero same-question companion petitions (`petitions: []` out of 15,608 indexed).

### C. Synthesis of Grant Probability (`0.06`)
Balancing the upward signal of the October 19, 2026 Call for a Response against the unpublished Rule 47.6 summary affirmance below, the mismatch between the *Hodges*/*Charas* split and Petitioners' core flight-cancellation claims, the absence of any circuit split on third-party vendor ADA preemption, and the lack of amicus support yields a final grant probability of **`0.06` (6.0%)**—modestly above the 5.16% `baseline` risk-set anchor (`cert_anchor.rate`), but well below the 13.5% rate of the full 1-relist bucket.

## 4. Rationale for Secondary Claims and Distributions

- **`relist-increment` (`0.97`):** `context.json` freezes `distribution_count: 1`. Because the Court requested a response on October 19, 2026 (due November 18, 2026), the petition will be redistributed for conference once the Brief in Opposition is filed (or the time expires), raising the terminal distribution count to at least 2 in ~97% of scenarios (leaving a ~3% allowance for pre-distribution voluntary dismissal/settlement under Rule 46).
- **`cvsg-increment` (`0.015`):** Across the paid scored segment in `statpack.md`, only 180 of 14,189 petitions (1.27%) draw a CVSG. Given the unpublished Rule 47.6 affirmance and the lack of a split on vendor preemption, a CVSG after the BIO arrives is very unlikely (~1.5%).
- **`summary-disposition-route` (`0.08`):** Conditional on a grant, the Court would almost certainly set the case for plenary briefing and argument (~92%) to address the statutory scope of § 41713(b)(1); there is no pending Supreme Court case for which this petition is being held, leaving only an ~8% conditional probability of a summary GVR (e.g., to require the Fifth Circuit to articulate its reasoning).
- **`dissent-from-denial` (`0.02`) and `order-writers`:** Separate writings respecting the denial of certiorari are rare (~1–2% of denials), particularly where the decision below is a summary affirmance under circuit rule. I assign `0.02` overall to `dissent-from-denial`, with small individual writing probabilities led by Justice Thomas (`0.008`) and Justice Gorsuch (`0.006`) in light of their prior skepticism toward expansive atextual federal preemption doctrines, followed by Justice Alito (`0.003`), Justices Sotomayor and Jackson (`0.002` each), and Chief Justice Roberts and Justices Kagan, Kavanaugh, and Barrett (`0.001` each).
- **`big_case_score` (`0.55`):** Decoupled from the low grant probability, if the Court were to grant certiorari and decide whether the Airline Deregulation Act immunizes third-party enterprise software vendors from state-law tort liability for nationwide flight disruptions (arising out of the historic July 2024 CrowdStrike outage), the decision would carry substantial commercial and doctrinal importance (`0.55`).

## 5. Uncertainties and Where to Discount This Forecast

The primary uncertainty is that Respondents' Brief in Opposition is not yet filed (due November 18, 2026). While Respondents are represented by experienced Supreme Court counsel (Samantha Lee Chaifetz of DLA Piper LLP) who can be expected to highlight the Rule 47.6 unpublished posture and the disconnect between the *Hodges*/*Charas* split and flight-delay claims, we do not yet know whether Respondents will request extensions of time, whether amicus briefs might still be filed if the BIO deadline is extended, or which specific Justice requested the response on October 19, 2026.
