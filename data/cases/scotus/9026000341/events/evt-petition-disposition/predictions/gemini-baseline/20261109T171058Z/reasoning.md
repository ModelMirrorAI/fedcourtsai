# Rationale for Prediction: *Spartan Securities Group, Ltd., et al. v. Securities and Exchange Commission* (No. 26-341)

## 1. Summary of Numbers

- **`granted`:** `0` (`predicted_disposition: "denied"`)
- **`probability` (`disposition`):** `0.11`
- **`big_case_score`:** `0.45`
- **`claims`:**
  - `disposition`: `0.11`
  - `relist-increment`: `0.96`
  - `cvsg-increment`: `0.01`
  - `summary-disposition-route`: `0.12`
  - `dissent-from-denial`: `0.08`
- **`order-writers`:** `Thomas: 0.055`, `Gorsuch: 0.025`, `Alito: 0.015`, `Kavanaugh: 0.005`, `Sotomayor: 0.003`, `Barrett: 0.003`, `Jackson: 0.003`, `Roberts: 0.002`, `Kagan: 0.002`

---

## 2. Provisioned Inputs Consulted and Empirical Anchoring

### A. Provisioned Record
We read the provisioned snapshot (`record/snapshots/2026-11-09.json`), `record/context.json`, `record/same-question.json` (which returned `petitions: []` over 15,608 indexed petitions at threshold 0.5), and all staged filings in `record/documents/` (`documents.json`, `questions-presented.txt`, `petition.txt`, `decision-below.txt`, and `lower-court-docket.txt`). We also verified via CourtListener MCP tools the full Eleventh Circuit opinion and Judge Tjoflat's dissent in *SEC v. Spartan Securities Group, Ltd.*, No. 22-13129 (11th Cir. Jan. 16, 2026) (because `decision-below.txt` was truncated at the 150,000-character pipeline cap inside the majority opinion), as well as the Supreme Court's recent decision in *Sripetch v. SEC*, No. 25-466, 608 U.S. ___, 146 S. Ct. 1403 (June 4, 2026), and its corpus prior via `uv run fedcourts query`.

### B. Statpack Base Rates (`metrics/statpack.md` and `context.json`)
- **Frozen Salience Band Anchor (`cert_anchor.rate`):** `context.json` freezes `band: "baseline"` under `salience_version: "sal-v8"`, with `distribution_count: 1`, `cvsg_date: null`, and `term: 2026`. The pooled 10-Term risk-set (`reached`) grant rate for `baseline` over Terms strictly preceding OT2026 (OT2017–OT2025) is **`5.16%`** (`0.0515879`, over `n = 12,658` weighted resolved petitions in the `baseline` risk set across OT2017–OT2025: 4.0% in OT2025 [`n=1290`], 6.0% in OT2024 [`n=1243`], 6.0% in OT2023 [`n=1283`], 5.9% in OT2022 [`n=1183`], 5.7% in OT2021 [`n=1469`], 4.7% in OT2020 [`n=1697`], 4.7% in OT2019 [`n=1369`], 4.8% in OT2018 [`n=1509`], and 5.0% in OT2017 [`n=1615`]).
- **Modern Discretionary-Cert Petitions Overall:** Across `n = 45,537` resolved modern cert petitions, the grant family (`granted` + `gvr`) is `2.8%` (1.4% `granted`, 1.4% `gvr`, 95.2% `denied`, 2.0% `dismissed`).
- **Originating Circuit (`ca11`):** In the paid/IFP modern cert cut, `ca11` sits at `3.3%` grant family (`1.2%` granted, `2.1%` gvr, `94.9%` denied over `n = 3,954` resolved; `4.2%` grant family in the court-including-state-courts table over `n = 3,072`).
- **Relist Count Cut (Paid Scored Segment):** Petitions ending with `0` relists (1 distribution) grant at `1.8%` (`1.3%` granted, `0.5%` gvr over `n = 10,204`), whereas petitions reaching `1` relist (2 distributions—which this petition will reach once the called-for response is filed and distributed) grant at `13.5%` (`8.3%` granted, `5.2%` gvr over `n = 2,532`).
- **Amicus-Brief Count Cut (Paid Scored Segment):** Petitions with `1` cert-stage amicus brief (matching this docket's October 15, 2026 brief from Investor Choice Advocates Network) have a marginal grant-family rate of `14.9%` (`10.2%` granted, `4.7%` gvr over `n = 1,159`), compared to `3.8%` (`2.0%` granted, `1.8%` gvr over `n = 11,109`) for `0` amicus briefs.
- **CVSG Status Cut (Paid Scored Segment):** `none` has a `6.4%` grant-family rate (`4.1%` granted, `2.3%` gvr over `n = 13,550`).

---

## 3. Upward Adjustments from the `5.16%` Anchor

Several concrete features in the snapshot and filings push `P(grant)` above the `5.16%` `baseline` risk-set anchor:
1. **Call for a Response (CFR) After Initial SG Waiver:** The Solicitor General waived the SEC's right to respond on October 9, 2026. Six days later (October 15, 2026), Investor Choice Advocates Network (ICAN) filed an amicus brief. Two days after initial distribution on October 21, 2026 (`distribution_count: 1`), the Court requested a response on October 23, 2026 (due November 23, 2026). Because the petition will be redistributed after the Brief in Opposition arrives, its true trajectory already tracks the `1`-relist (`rescheduled`/`elevated`) cohort (`13.5%` terminal grant-family rate in the relist table) rather than a waived single-distribution denial.
2. **Direct Overlap with the Question Expressly Reserved in *Sripetch v. SEC* (June 2026):** Just five months ago in *Sripetch v. SEC*, 608 U.S. ___, 146 S. Ct. 1403 (2026), the Court held that SEC disgorgement does not require investor pecuniary loss, while expressly reserving whether 15 U.S.C. § 78u(d)(7) permits the SEC to depart from *Liu v. SEC*, 591 U.S. 71 (2020), and deposit disgorged funds into the U.S. Treasury rather than returning them to victims. Justice Thomas's concurrence in *Sripetch*—which specifically cited ICAN's amicus brief in that case—stated that "[w]e will soon need to address whether disgorgement under § 78u(d)(7) is a legal remedy" and criticized Treasury disgorgement. Here, the Eleventh Circuit squarely held (Pet. App. 62a–68a) that §§ 78u(d)(3)(A)(ii) and (d)(7) authorize disgorgement to the Treasury unconstrained by § 78u(d)(5)'s "for the benefit of investors" limitation, deepening the doctrinal tension among the Fifth Circuit (*SEC v. Hallam*, 42 F.4th 316 (5th Cir. 2022)), the Second Circuit (*SEC v. Ahmed*, 72 F.4th 379 (2d Cir. 2023); *SEC v. Govil*, 86 F.4th 89 (2d Cir. 2023)), and the Eleventh Circuit.
3. **Experienced Counsel and Amicus Support:** Petitioners are represented by the New Civil Liberties Alliance (including former SEC enforcement assistant director Russell G. Ryan) and supported by ICAN at the cert stage.

---

## 4. Downward Adjustments: Severe Vehicle Defects on Both Questions Presented

Despite the CFR and the surface appeal of Question Presented 2, close inspection of the Eleventh Circuit opinion (`decision-below.txt`) and the petition (`petition.txt`) reveals decisive vehicle flaws that the Solicitor General's Brief in Opposition will highlight, pulling `P(grant)` down to `0.11`:

### A. Vehicle Flaws on Question Presented 2 (Disgorgement to the Treasury)
1. **Petitioners Stipulated That Investor Distribution Was Infeasible:** In the district court, Petitioners *stipulated* that "[a] distribution to investors of the disgorgement amount requested would be infeasible" (`decision-below.txt`, slip op. at 23, 70). Because Petitioners stipulated to infeasibility, this case cannot resolve the question left open in *Liu* (and noted again in *Sripetch*) regarding what evidentiary showing the SEC must make to prove that distributing funds to harmed investors is infeasible.
2. **Independent Alternative Equitable Holding Below:** Both the district court and the Eleventh Circuit upheld the $114,520 disgorgement award against Island on **two independent grounds**: (a) statutory authority under §§ 78u(d)(3)(A)(ii) and (d)(7) without § 78u(d)(5)'s investor-benefit requirement (Slip op. at 62–68), **and** (b) in the alternative, even under traditional equitable principles, where distributing ill-gotten profits to investors is stipulated to be infeasible, equity does not allow the wrongdoer to keep its ill-gotten gains and permits directing the funds to the Treasury (Slip op. at 24–25, 68–70). Because of that alternative holding, resolving whether § 78u(d)(7) frees the SEC from *Liu*'s equitable limits would not change the outcome unless the Court also held that traditional equity compels leaving ill-gotten gains with a fraudster whenever victim distribution is stipulated to be infeasible.
3. **Non-Preservation of the Seventh Amendment Issue Flagged by Justice Thomas:** In *Sripetch*, Justice Thomas urged the Court to address the circuit split between *Hallam* (5th Cir.) and *Ahmed* (2d Cir.) over whether § 78u(d)(7) is a "legal" remedy triggering the Seventh Amendment right to a jury trial. Here, however, Petitioners did **not** preserve or raise a Seventh Amendment challenge to disgorgement (they raised a Seventh Amendment challenge below only to civil penalties, which they abandoned in their cert petition; see `petition.txt` at 31 n.9). Moreover, *Hallam* held that § 78u(d)(7) expands the SEC's authority beyond *Liu*—meaning the Fifth Circuit and the Eleventh Circuit reach the *same bottom-line result* allowing Treasury deposit.
4. **Narrow Party Posture and Timing After *Sripetch*:** Only Island Capital Management (an out-of-business transfer agent) was ordered to pay disgorgement ($114,520 in fees received directly from the shell-company fraudsters Mirman and Rose, after deducting legitimate expenses). Having just decided *Sripetch* in June 2026, the Court is unlikely to grant a second SEC disgorgement case immediately afterward on a stipulated-infeasibility record.

### B. Vehicle and Merits Flaws on Question Presented 1 (Section 10(b) "In Connection With")
1. **Trial Record Refutes the Factual Premise of QP 1:** Question Presented 1 asks whether statements made to an SRO (FINRA on Form 211) "without proof that they were ever seen by any investor" satisfy Section 10(b). Yet the Eleventh Circuit explicitly held (`decision-below.txt`, slip op. at 41 & n.7, 46) that the Form 211 cover page signed by Petitioners Dilley and Eldred expressly stated that FINRA may provide copies of the Form 211 and accompanying submissions "to the public upon request," and Eldred testified at trial that he believed the Form 211 applications were publicly available. Viewing the trial evidence in the light most favorable to the jury's verdict under Rule 50(b), the panel concluded that a reasonable jury could find the Form 211 submissions were accessible to the investing public.
2. **No Circuit Split on "In Connection With" in SEC Enforcement Actions:** Under *SEC v. Zandford*, 535 U.S. 813, 819–22 (2002), and *United States v. Naftalin*, 441 U.S. 768, 772–73 (1979), an SEC enforcement action under Section 10(b) does not require proof of individual investor reliance. False statements to FINRA and DTC that were necessary to initiate public quotations and electronic clearing—followed immediately by Spartan acting as exclusive market-maker quoting and selling the securities—plainly coincide with securities transactions.
3. **Judge Tjoflat's Dissent Below Was Unrelated to Either Question Presented:** Verification of the full Eleventh Circuit opinion on CourtListener confirmed that Judge Tjoflat's dissent rested exclusively on civil procedure ("shotgun pleading" under Rules 8(a) and 9(b)), an issue Petitioners omitted from their Questions Presented.

---

## 5. Justification for Subsidiary Claims and `big_case_score`

- **`relist-increment: 0.96`:** Because the Court called for a response on October 23, 2026 after the first distribution (`distribution_count: 1`), the petition will be redistributed for conference once the SEC files its Brief in Opposition, barring an unlikely voluntary withdrawal or settlement (`~4%`).
- **`cvsg-increment: 0.01`:** The Solicitor General already represents Respondent SEC and has been ordered to file a response.
- **`summary-disposition-route: 0.12`:** Conditional on a grant, plenary review is far likelier (`88%`) than a summary disposition or GVR (`12%`), because *Sripetch* ruled in the SEC's favor and explicitly left open the § 78u(d)(7) Treasury issue.
- **`dissent-from-denial: 0.08` & `order-writers`:** Given Justice Thomas's June 2026 concurrence in *Sripetch* (citing ICAN's amicus brief) and the October 23, 2026 CFR following ICAN's amicus brief here, there is an elevated `8%` chance that a Justice—most likely Justice Thomas (`0.055`), Justice Gorsuch (`0.025`), or Justice Alito (`0.015`)—authors a dissent from or statement respecting the denial of certiorari.
- **`big_case_score: 0.45`:** If decided on the merits, the scope of SEC disgorgement to the Treasury under 15 U.S.C. § 78u(d)(7) and Section 10(b) liability for broker-dealer regulatory filings would be moderately significant for federal securities enforcement and administrative remedies (`0.45`), though narrower than major constitutional or nationwide structural cases.
