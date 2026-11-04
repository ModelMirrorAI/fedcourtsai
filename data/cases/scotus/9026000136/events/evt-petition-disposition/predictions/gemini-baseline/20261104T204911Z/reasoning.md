# Rationale for Prediction Numbers: *Tesla, Inc. v. Granite Vehicle Ventures LLC, et al.* (No. 26-136)

## 1. Summary of Numbers

- **`granted` / `predicted_disposition`:** `0` / `"denied"`
- **`probability` (`disposition`):** `0.06`
- **`relist-increment`:** `0.12`
- **`cvsg-increment`:** `0.01`
- **`summary-disposition-route`:** `0.25`
- **`dissent-from-denial`:** `0.03`
- **`big_case_score`:** `0.45`

---

## 2. Base-Rate Anchoring (`metrics/statpack.md` and `record/context.json`)

We read the provisioned snapshot (`record/snapshots/2026-11-04.json`), `record/context.json`, `record/same-question.json`, and all four text filings in `record/documents/` (`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, and `cert-reply.txt`, all non-empty and non-OCR).

Per `record/context.json`, this cell is in `forward` mode at `moment: distribution` (`cutoff: null`), with `salience_version: "sal-v6"`, `band: "elevated"`, `distribution_count: 2`, `cvsg_date: null`, and `term: 2026`. The frozen cert skill anchor in `context.json` (`cert_anchor.rate`) is **`0.24838227974116475` (~24.84%)**, pooled over the 10 prior Terms (`lookback_terms: 10`, OT2016–OT2025) for the `elevated` band's bracketed `reached` risk set.

In `metrics/statpack.md`, we cross-check the relevant cuts:
- **Segment base rate by salience band (`sal-v6`):** Across OT2017–OT2025, the `elevated` band's bracketed `reached` grant rate ranges from 21.3% (`n=207` in OT2019) to 27.8% (`n=230` in OT2021), with OT2025 at 21.7% (`n=175`) and OT2024 at 27.7% (`n=213`).
- **Cert petitions by relist count (paid scored segment):** Bucket `1` (which corresponds to `distribution_count = 2`, i.e., one additional distribution entry beyond the first, including pre-conference reschedules) has a resolved grant-family rate of **13.5%** (`granted` 8.3% + `gvr` 5.2%, ` denied` 85.5%, `n=2532` resolved), compared to 1.8% (`granted` 1.3% + `gvr` 0.5%, `n=10204` resolved) for bucket `0`.
- **Cert petitions by CVSG status (paid scored segment):** For `none` (no CVSG), the grant-family rate is **6.4%** (`granted` 4.1% + `gvr` 2.3%, `n=13549` resolved).
- **Cert petitions by amicus-brief count (paid scored segment):** The docket shows three amicus filings (Askeladden L.L.C.; US*MADE et al.; Unified Patents LLC), placing it in the `2+` bucket, where the marginal grant-family rate is **22.7%** (`granted` 18.2% + `gvr` 4.5%, `n=1446` resolved).
- **Modern cert petitions by originating circuit (`cafc`):** Federal Circuit petitions have a resolved grant-family rate of **4.5%** (`granted` 3.0% + `gvr` 1.5%, `denied` 92.5%, `dismissed` 3.0%, `n=907` resolved).

---

## 3. Case-Specific Adjustments from the 24.84% Anchor

Starting from the `0.2484` `elevated`-band anchor, three strong negative factors justify adjusting `P(grant)` down to `0.06`:

### A. Pre-Conference Reschedule Rather Than a True Conference Relist (`-0.08`)
As `metrics/statpack.md` notes, `distribution_count` is an upper bound on true relists because a pre-conference reschedule adds a distribution entry. Here, `record/snapshots/2026-11-04.json` shows that the petition was distributed on October 14, 2026 for the November 6, 2026 Conference, marked "Rescheduled" on October 22, 2026 (fifteen days *before* the November 6 conference took place), and redistributed on November 4, 2026 for the December 4, 2026 Conference. Thus, the Justices have not yet considered and relisted this petition at a conference; the reschedule appears to be administrative coordination (likely aligning the conference date with the other pending PTAB discretionary-denial petitions, *Intel Corp. v. Squires*, No. 26-73, and *Kahoot! AS v. Interstellar Inc.*, No. 26-198). Even across all `relist_bucket = 1` cases in the statpack, the grant-family rate is 13.5%, well below the 24.84% `elevated` risk-set average (which is pulled up by petitions that go on to multiple relists or CVSGs).

### B. October 19, 2026 Denial of Lead Companion Petition *Google LLC v. VirtaMove, Corp.* (No. 25-1230) (`-0.08`)
In both the Petition (pp. 29–30) and the Reply Brief (pp. 10–12, filed October 13, 2026), Tesla relies heavily on the pendency of three companion petitions presenting the same question: *Google LLC v. VirtaMove, Corp.* (No. 25-1230), *Intel Corp. v. Squires* (No. 26-73), and *Kahoot! AS v. Interstellar Inc.* (No. 26-198). Using `uv run fedcourts query --court scotus --docket-number 25-1230`, we verified that on **October 19, 2026**—after Tesla's reply brief was filed, and before the November 4, 2026 snapshot—the Court **denied certiorari** in *Google LLC v. VirtaMove, Corp.* (`scotus/73265705`). Like *Tesla*, *Google* arose on a mandamus petition from the Federal Circuit challenging PTAB discretionary denials of IPR institution as contrary to the AIA, had `distribution_count: 2`, and was supported by seven amicus briefs. That denial follows the Court's unbroken series of certiorari denials in prior challenges to the PTAB's *Fintiv* framework and § 314(d) reviewability bar, including *Intel Corp. v. Vidal*, 144 S. Ct. 548 (2024) (No. 23-135), *Intel Corp. v. VLSI Tech. LLC*, 142 S. Ct. 1363 (2022) (No. 21-888), *Mylan Labs. Ltd. v. Janssen Pharmaceutica, N.V.*, 142 S. Ct. 874 (2022) (No. 21-202), and *Apple Inc. v. Optis Cellular Tech., LLC*, 142 S. Ct. 859 (2022) (No. 21-118).

### C. Severe Vehicle Flaws and Mandamus Posture (`-0.03`)
Even if the Court were inclined to grant certiorari in one of the remaining pending petitions (*Intel Corp. v. Squires*, No. 26-73, or *Kahoot! AS v. Interstellar Inc.*, No. 26-198), *Tesla* is an inferior vehicle:
1. **Mandamus Standard Unaddressed:** The Federal Circuit denied relief in a short, nonprecedential per curiam order (*In re Tesla, Inc.*, No. 2026-116, 2026 WL 555080) on a petition for a writ of mandamus. As the Solicitor General points out in the Brief in Opposition (pp. 10–12), Tesla failed even to argue the three prerequisites for mandamus under *Cheney v. United States District Court*, 542 U.S. 367, 380–81 (2004).
2. **Adequate Alternative Remedies and Ongoing *Ex Parte* Reexaminations:** While seeking mandamus, Tesla requested *ex parte* reexamination of all three patents, and the USPTO has already ordered *ex parte* reexamination of two of them (`90/019,990` and `90/019,991`) while the third request (`90/020,256`) is pending. Tesla is also actively litigating invalidity in the Northern District of California infringement suit.
3. **Superior APA Companion Vehicle:** Unlike *Tesla*, *Intel Corp. v. Squires* (No. 26-73) arises from a published, precedential Federal Circuit decision in a direct APA challenge to the *Fintiv* instructions (*Apple Inc. v. Squires*, 166 F.4th 1349 (Fed. Cir. 2026)), unencumbered by the demanding mandamus standard or the § 314(d) bar on appealing individual institution determinations.

We retain a 6.0% (`0.06`) grant probability for the residual possibility that the Court grants review of the PTAB's discretionary-denial practices at the December 4, 2026 conference (either consolidating *Tesla* with *Intel*/*Kahoot!* or holding *Tesla* and later issuing a GVR).

---

## 4. Rationale for Secondary Claims and Big-Case Score

- **`relist-increment` (`0.12`):** Because the petition is scheduled for the December 4, 2026 Conference alongside or near *Intel Corp. v. Squires* (No. 26-73) and *Kahoot!* (No. 26-198), the most likely outcome (~88%) is a straightforward denial after that conference without another distribution. However, if the Court relists *Intel* or *Kahoot!* at the December 4 conference—or in the small event it grants *Intel* and holds *Tesla*—*Tesla* could be distributed at least once more.
- **`cvsg-increment` (`0.01`):** The United States (USPTO Director John A. Squires, represented by Solicitor General D. John Sauer) is already a respondent and has filed a Brief in Opposition. A CVSG is virtually impossible (`0.01`).
- **`summary-disposition-route` (`0.25`):** Conditional on *Tesla* receiving a grant-family disposition, there is roughly a 25% chance it takes the form of a GVR (after a hold for *Intel Corp. v. Squires*, No. 26-73, if *Intel* were granted and decided in petitioners' favor) versus a 75% chance of plenary review (either standalone or consolidated).
- **`dissent-from-denial` (`0.03`) and `order-writers`:** Separate writings on patent/PTAB certiorari denials are rare, and *Google v. VirtaMove* (No. 25-1230) was denied on October 19, 2026 with no recorded dissent. We assign a 3% probability of any separate writing, weighted slightly toward Justices Gorsuch (`0.015`) and Thomas (`0.008`), who have most frequently written separately on PTAB and administrative-reviewability issues.
- **`big_case_score` (`0.45`):** While this individual mandamus petition is a narrow vehicle, the underlying question—whether the USPTO Director can categorically or discretionarily refuse to institute IPRs based on extra-statutory parallel-litigation and settled-expectations rules—is closely watched by major technology, automotive, and pharmaceutical companies and has drawn coordinated amicus support.
