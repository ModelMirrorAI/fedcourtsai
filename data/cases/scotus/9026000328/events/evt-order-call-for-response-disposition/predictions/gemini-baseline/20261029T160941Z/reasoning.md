# Certiorari Rationale: *Charter Consolidated, Ltd., et al. v. Cape Intermediate Holdings Limited, et al.* (No. 26-328)

**Event:** `evt-order-call-for-response-disposition` (`moment: response-requested`)  
**Input Snapshot:** `2026-10-27.json` (provisioned alongside `context.json`, `documents/questions-presented.txt`, `documents/petition.txt`, `documents/appendix.txt`, and `related/26-350.json`)  
**Prediction:** `predicted_disposition = "denied"`, `granted = 0`, `probability = 0.06`  
**Big Case Score:** `0.35`

---

## 1. Anchor and Base Rates (`metrics/statpack.md`)

From `record/context.json`, this cell is in `forward` mode with `term = 2026`, `band = "baseline"`, `salience_version = "sal-v4"`, `distribution_count = 1`, `cvsg_date = null`, and `vide_links = ["26-350"]`.

1. **Salience Band Anchor (`sal-v4`):**  
   In `metrics/statpack.md` (*Segment base rate by salience band (sal-v4)*), pooling the bracketed `reached` grant rates for the `baseline` band across all rendered Terms strictly preceding OT2026 (OT2017–OT2025, 9 Terms):
   - OT2025: 4.0% ($n=1314$)
   - OT2024: 5.9% ($n=1274$)
   - OT2023: 5.9% ($n=1312$)
   - OT2022: 5.9% ($n=1196$)
   - OT2021: 5.7% ($n=1500$)
   - OT2020: 4.5% ($n=1740$)
   - OT2019: 4.7% ($n=1399$)
   - OT2018: 4.8% ($n=1529$)
   - OT2017: 4.9% ($n=1649$)
   
   Across the pooled strictly-prior denominator of $n = 12,913$ weighted resolved petitions, the `baseline` `[reached]` grant rate is **5.11%** (~5.1%).

2. **Signal Cuts in `metrics/statpack.md`:**
   - **Modern discretionary-cert petitions overall:** 692 `granted` + 590 `gvr` out of 44,777 resolved (**2.86%** grant family; 95.1% denied).
   - **Relist count (paid scored segment):** Bucket `0` ($n = 10,203$ resolved) has a terminal grant-family rate of **1.8%** (1.3% granted, 0.5% GVR, 96.8% denied), whereas bucket `1` ($n = 2,538$ resolved) rises to **13.7%** (8.5% granted, 5.2% GVR, 85.3% denied). Here, the petition has been distributed once (`distribution_count = 1` for the November 6, 2026 conference), and because the Court called for a response on October 27, 2026, it will be redistributed once the briefs in opposition are filed.
   - **CVSG status (paid scored segment):** `none` ($n = 13,556$ resolved) has a **6.4%** grant-family rate (4.1% granted, 2.3% GVR, 92.4% denied).
   - **Cert amicus-brief count (paid scored segment):** The snapshot records three cert-stage amicus briefs filed on October 15, 2026 (Washington Legal Foundation, Atlantic Legal Foundation, and National Union Fire Insurance Co.), placing this petition in the `2+` bucket ($n = 1,449$ resolved), which carries a marginal grant-family rate of **22.9%** (18.4% granted, 4.5% GVR, 76.0% denied).
   - **Originating court:** Petitions from state supreme courts not separately broken out in the top originating-court rows (`(none)` in the circuit table, $n = 11,615$ resolved) grant at **1.3%** (0.6% granted, 0.7% GVR, 96.4% denied).

---

## 2. Case-Specific Adjustments from the Anchor

### Upward Factors
- **Call for a Response (`moment: response-requested`) and Companion Petition (`26-350`):** Both respondents—plaintiffs John and Margaret Tibbs and Receiver Peter D. Protopapas—filed waivers of the right to respond on October 9 and October 14, 2026. On October 27, 2026, after the petition was distributed for the November 6, 2026 conference, the Court requested a response (due November 27, 2026) in both No. 26-328 and its companion Vide petition, *Altrad Investment Authority S.A.S., et al. v. Cape Intermediate Holdings Limited, et al.* (No. 26-350, `related/26-350.json`).
- **Experienced Supreme Court Counsel and Amicus Support:** Petitioners in No. 26-328 are represented by Amir C. Tayrani (Gibson, Dunn & Crutcher LLP), Petitioners in companion No. 26-350 are represented by Kannon K. Shanmugam (Paul, Weiss), and three business/legal foundation amici filed briefs supporting certiorari.
- **Overlapping Pending Petitions from the Third Circuit:** The Receiver and the Official Committee of Talc Claimants recently filed certiorari petitions challenging *In re Whittaker, Clark & Daniels, Inc.*, 176 F.4th 241 (3d Cir. 2026), docketed as Nos. 26-159 and 26-263. Because Petitioners rely heavily on *Whittaker* to allege a split, it is natural for the Court to call for a response rather than dispose of the petitions on waivers.

### Downward Factors (Decisive Vehicle and Threshold Obstacles)
1. **Recent Denial of Certiorari in *Atlas Turner, Inc. v. Welch* (No. 25-213):**  
   Corpus retrieval (`uv run fedcourts query --court scotus --docket-number 25-213 --include-open --full`) and the petition's related-cases disclosure confirm that on **January 12, 2026**, this Court denied certiorari after two distributions in *Atlas Turner, Inc. v. Welch*, No. 25-213. *Welch* challenged the South Carolina Supreme Court's foundational decision (*Welch v. Advance Auto Parts, Inc.*, 445 S.C. 640, 916 S.E.2d 320 (2025)) upholding the same South Carolina trial court's appointment of the same receiver (Peter Protopapas) over an out-of-state/foreign asbestos defendant under S.C. Code § 15-65-10(5) ("moral fraud"). Crucially, in *Welch*, the petitioner was the foreign corporation placed into receivership itself (*Atlas Turner, Inc.*), supported by three amicus briefs (including the U.S. Chamber of Commerce, ATRA, and National Union Fire Insurance Co.). The Court's recent denial in *Welch* strongly undercuts the likelihood that it will grant review in a follow-on application of *Welch*.

2. **Severe Finality Defect Under 28 U.S.C. § 1257(a):**  
   In `documents/appendix.txt` (Pet. App. 1a–35a), the South Carolina Supreme Court's May 27, 2026 decision is explicitly interlocutory. It remands the case to the circuit court for trial on the merits, noting that:
   - Personal jurisdiction over both CIHL and Petitioners remains interlocutory and open to merits adjudication at trial (Pet. App. 12a: "The trial court still has to review the issue on the merits, and the parties, including Appellants, may present additional evidence as to this issue at trial");
   - Choice of law and the merits of the Receiver's third-party alter-ego/amalgamation and unjust-enrichment claims remain undecided and must be litigated on remand (Pet. App. 22a, 28a); and
   - Petitioners' affirmative defense based on the mutual release remains open for adjudication at trial (Pet. App. 32a).
   
   Petitioners' reliance on *Cox Broadcasting Corp. v. Cohn*, 420 U.S. 469 (1975), and *Clark v. Williard*, 292 U.S. 112 (1934) (`documents/petition.txt`, Pet. 1, 34–35), is unpersuasive: *Clark* involved post-judgment execution by judgment creditors, whereas an order appointing or refusing to vacate a pre-judgment receiver pendente lite is a classic interlocutory order. Under *Cox*'s fourth category, reversal on the federal question here would not terminate the underlying litigation, and Petitioners may prevail in state court on numerous non-federal grounds at trial.

3. **Third-Party Standing Defect:**  
   Cape Intermediate Holdings Limited (CIHL)—the English corporation over whose South Carolina assets/claims the pre-judgment receiver was appointed—has never appeared in the South Carolina courts and is not a petitioner here (Pet. App. 12a, 28a, 50a). Instead, Petitioners are *third-party defendants* sued by the Receiver for unjust enrichment and alter-ego liability. As the South Carolina Supreme Court emphasized (Pet. App. 28a, 30a–31a, 49a–50a), Petitioners deny being alter egos of or affiliated with CIHL while attempting to assert CIHL's internal-governance and Due Process rights as a shield against third-party claims. Under *Kowalski v. Tesmer*, 543 U.S. 125 (2004), this third-party standing posture is a major vehicle flaw.

4. **Preservation Defects Flagged by the State Supreme Court:**  
   In its August 25, 2026 order denying a stay of the remittitur (Pet. App. 48a–49a), the South Carolina Supreme Court explicitly questioned whether Petitioners preserved their Dormant Commerce Clause and Due Process arguments below and stated outright that "Appellants' argument that the receivership order violates what they contend is the federal government's exclusive jurisdiction over foreign relations has never been presented to us before and cannot be raised now."

5. **Illusory Conflict with *Whittaker*:**  
   In *In re Whittaker, Clark & Daniels, Inc.*, 176 F.4th 241 (3d Cir. 2026), the Third Circuit held that a South Carolina receivership order (a) did not by its terms divest a New Jersey corporation's board of authority to file a federal Chapter 11 bankruptcy petition, and (b) could not under Full Faith and Credit displace the board's authority under New Jersey law to authorize a bankruptcy filing without recognition in New Jersey. Here, by contrast, the South Carolina Supreme Court **modified and narrowed** the pre-judgment receivership order so that the Receiver "may only operate to collect insurance assets and pursue such legal and equitable claims the corporation may have that can result in the receipt of assets responsive to the Tibbs' pending claims" within the South Carolina action (Pet. App. 27a, 47a). It does not displace CIHL's board outside South Carolina or prevent CIHL from initiating insolvency proceedings in England.

---

## 3. Calibration of Claims and Distributions

- **`probability` / `disposition` = `0.06`:** Starting from the 5.1% `baseline` `[reached]` anchor, the upward pressure from the Call for a Response, three amicus briefs, and elite counsel is nearly counterbalanced by the recent denial in *Welch* (No. 25-213) and the severe § 1257(a) finality, third-party standing, preservation, and split-distinguishability obstacles that respondents will highlight in their forthcoming briefs in opposition.
- **`relist-increment` = `0.98`:** Because the petition was distributed once (`distribution_count = 1`) for the November 6, 2026 conference and the Court called for a response due November 27, 2026, the petition is virtually certain to be distributed again once the brief in opposition is filed (barring settlement or withdrawal).
- **`cvsg-increment` = `0.02`:** A CVSG is very unlikely in an interlocutory state-court receivership dispute where the Court recently denied certiorari without a CVSG in *Welch* (No. 25-213) and where the South Carolina Supreme Court held that any foreign-relations argument was never raised below.
- **`summary-disposition-route` = `0.10`:** Conditional on a grant, plenary review is by far the likelier route (90%), with a 10% conditional probability of a GVR (for instance, if the Court were to grant one of the *Whittaker* petitions, Nos. 26-159 or 26-263, and later GVR).
- **`dissent-from-denial` = `0.04` and `order-writers`:** Conditional on denial, there is a small (~4%) chance that a Justice (most plausibly Justice Thomas at 1.5%, Justice Alito at 1.5%, or Justice Gorsuch at 1.0%) authors or joins a dissent or statement respecting the denial of certiorari given the extraterritoriality and due-process themes, though no Justice wrote when *Welch* (No. 25-213) was denied.
- **Main uncertainties:** Because this is a `moment: response-requested` cell, no brief in opposition has been filed yet; my assessment of how respondents will frame the § 1257(a) finality, standing, and preservation objections is drawn from the South Carolina Supreme Court's May 27, 2026 opinion and August 25, 2026 order in `documents/appendix.txt`.
