# Prediction Rationale: *Amazon Logistics, Inc., et al. v. Dirk Clinton, et al.* (No. 26-47)

## 1. Bottom-Line Numbers

- **`granted`:** `0` (`predicted_disposition`: `"denied"`)
- **`probability` (P(any grant)):** `0.06` (decomposed as ~3.5% `gvr` and ~2.5% plenary `granted`, vs. 94.0% `denied`)
- **`claims`:**
  - `disposition`: `0.06`
  - `relist-increment`: `0.98`
  - `cvsg-increment`: `0.01`
  - `summary-disposition-route`: `0.58`
  - `dissent-from-denial`: `0.02`
- **`big_case_score`:** `0.55`

---

## 2. Base-Rate Anchor & Structural Conditioning

From `record/context.json` and `metrics/statpack.md`:

- **Frozen Cert Anchor (`context.cert_anchor`):** `record/context.json` freezes `band: "baseline"` under `salience_version: "sal-v7"` (`term: 2026`, `distribution_count: 1`, `cvsg_date: null`, `amicus_briefs: null`) with `cert_anchor.rate = 0.051512996760685784` (**5.15%** over `lookback_terms: 10`, digest `sha256:17f38fd88c014731f55c236faa1e9878525fc40e69898293166611c0ffb59f25`). In `metrics/statpack.md` ("Segment base rate by salience band (sal-v7)"), the bracketed `reached` grant rate for the `baseline` band across the nine rendered prior Terms (OT2017–OT2025) ranges between **4.0%** (OT2025, `n=1289`) and **6.0%** (OT2023 `n=1283`, OT2024 `n=1243`), pooling to the **5.15%** anchor.
- **Signal Cuts in `metrics/statpack.md`:**
  - **Modern discretionary-cert petitions by disposition:** `denied` 42,890, `dismissed` 919, `granted` 638, `gvr` 637 (overall modern cert grant-family rate ~2.8% across paid and IFP).
  - **Relist count (paid scored segment):** Bucket `0` (1 distribution, no relist at disposition) has a resolved base rate of `denied 96.8%, dismissed 1.3%, granted 1.3%, gvr 0.5%` (`n=10,204` resolved). Bucket `1` (2 distributions) has `denied 85.5%, granted 8.3%, gvr 5.2%, dismissed 1.0%` (`n=2,532` resolved). Note that those buckets condition on *terminal* distribution counts.
  - **CVSG status (paid scored segment):** `none` (`n=13,549` resolved) resolves `denied 92.4%, granted 4.1%, gvr 2.3%, dismissed 1.2%` (6.4% grant family).
  - **Amicus-brief count (paid scored segment):** `0` amicus briefs (`n=11,109` resolved) resolves `denied 95.0%, granted 2.0%, gvr 1.8%, dismissed 1.3%` (3.8% grant family), compared with `14.8%` for 1 amicus (`n=1,158`) and `22.7%` for 2+ amici (`n=1,446`).
  - **Originating court:** State-court petitions grant at much lower rates than federal circuit petitions; in `Petitions by originating court (incl. state courts)`, `Court of Appeal of California, Second Appellate District` (`n=234`) is `denied 91.5%, dismissed 5.1%, gvr 3.0%, granted 0.4%`, and `Court of Appeal of California, First Appellate District` (`n=103`) is `denied 93.2%, dismissed 4.9%, granted 1.9%`.

---

## 3. Case-Specific Adjustments from the 5.15% Anchor

### A. Upward Adjustment for the August 18, 2026 Call for Response (CFR)

The provisioned snapshot (`record/snapshots/2026-11-06.json`) shows that after Amazon filed its petition on June 29, 2026, Respondents (represented by Jennifer Dale Bennett of Gupta Wessler LLP) filed a waiver on August 10, 2026. The petition was distributed on August 12, 2026 for the September 28, 2026 Long Conference, and six days later—on August 18, 2026—the Court requested a response (subsequently extended twice, now due November 16, 2026).

A Call for Response after an initial waiver indicates that at least one chambers (or the pool memo writer) flagged the petition as warranting a Brief in Opposition rather than a summary denial on waiver. That procedural signal pushes the grant probability above a typical no-response `baseline` petition (~1–2%) and slightly above the unconditioned `baseline` reached anchor (**5.15%**), particularly because the decision below (App. 4a n.4, 8a–9a & n.10) expressly borrowed its class definition from *Flowers Foods, Inc. v. Brock*, No. 24-935, while *Brock* was still pending in this Court.

### B. Why Grant Probability Remains Low (`0.06` Total: ~3.5% GVR, ~2.5% Plenary)

Despite the CFR, several strong legal, procedural, and institutional considerations observed in `petition.txt`, `appendix.txt`, and recent precedent keep the probability of a grant (whether GVR or plenary review) modest at **6.0%**:

1. ***Flowers Foods v. Brock* Unanimously Affirmed in Favor of the Worker and Cited *Rittmann* Neutrally:**
   In *Flowers Foods, Inc. v. Brock*, 146 S. Ct. 1358 (May 28, 2026), Justice Gorsuch wrote for a unanimous (9–0) Court affirming the Tenth Circuit and holding that delivery drivers who transport goods on an intrastate leg of an interstate journey can qualify for FAA § 1's exemption without crossing state lines or interacting with vehicles that do. As Justice Gorsuch noted, *Brock* was the **fourth** consecutive case since 2019 (*New Prime*, *Saxon*, *Bissonnette*, and *Brock*) in which the Court unanimously rejected employer efforts to narrow Section 1.
   Amazon relies on Part II of *Brock* (146 S. Ct. at 1366), where the Court noted that Flowers had mentioned other facts in passing—such as intermediate title transfers or independent business entities—that some lower courts had considered (citing *Rittmann v. Amazon.com, Inc.*, 971 F.3d 904, 916 (9th Cir. 2020), and *Immediato v. Postmates, Inc.*, 54 F.4th 67, 72, 78 (1st Cir. 2022)), but that Flowers had not asked the Court to decide their legal significance. Crucially:
   - *Brock* did **not** hold that pre-order warehouse storage or mixed local deliveries defeat the Section 1 exemption; on the contrary, it cited *Rittmann*—the very Ninth Circuit decision the California Court of Appeal followed here (App. 4a, 9a–13a)—without disapproval.
   - Because the California Court of Appeal ruled *in favor* of the workers, and *Brock* also ruled *in favor* of the worker, a GVR in light of *Brock* would be anomalous once Respondents' BIO points out that *Brock* rejected the employer's position. Indeed, subsequent published California Court of Appeal opinions (*Betanco v. Living Spaces Furniture, LLC*, June 25, 2026; *Doss v. Tesla, Inc.*, June 11, 2026) have already examined *Brock* and held that it supports California's application of *Rittmann* and *Carmona Mendoza v. Domino's Pizza, LLC*, 73 F.4th 1135 (9th Cir. 2023).

2. **No Circuit Split on Amazon Flex Last-Mile Package Drivers:**
   Every federal court of appeals to consider Amazon Flex drivers delivering packages from Amazon fulfillment centers has held that they are exempt under FAA § 1 (*Rittmann*, 971 F.3d at 915–917; *Waithaka v. Amazon.com, Inc.*, 966 F.3d 10, 26 (1st Cir. 2020)), and this Court denied certiorari in both *Rittmann* (141 S. Ct. 1374 (2021)) and *Waithaka* (141 S. Ct. 2791 (2021)), as well as in *Domino's Pizza, LLC v. Carmona* (144 S. Ct. 1391 (2024)). The Fifth and Seventh Circuit decisions Amazon cites (*Lopez v. Cintas Corp.*, 47 F.4th 428 (5th Cir. 2022); *Wallace v. Grubhub Holdings, Inc.*, 970 F.3d 798 (7th Cir. 2020)) involved uniform-rental route sales representatives and restaurant food couriers, and both opinions expressly distinguished last-mile parcel delivery drivers like those in *Rittmann* and *Waithaka*.

3. **Record and Vehicle Complications Below:**
   - **Unpublished intermediate state-court decision:** Both the California Court of Appeal and the California Supreme Court declined to publish the opinion below (App. 1a, 2a), limiting its precedential effect even within California.
   - **Undisputed cross-border customer orders and mixed AMZL/GSF record:** As the Superior Court's Statement of Decision (App. 20a–27a) and the Court of Appeal's opinion (App. 9a–13a) explain, Amazon's own declarations (Rodgers Decl., App. 28a–36a; Nickerson Decl., App. 37a–40a) acknowledged that goods delivered in AMZL brown-box blocks (32.6% of California Flex blocks) and many goods in GSF blocks (67.4% of blocks) originated outside California, and that even under Amazon's inventory statistics, approximately 12% of AMZL items were shipped across state lines *after* the customer placed the order (App. 32a ¶ 12), while the remaining items were shipped to California fulfillment centers based on Amazon's demand forecasting to fulfill anticipated customer orders. Under *Saxon*, 596 U.S. at 456, workers who "frequently" perform exempt interstate transportation work fall within Section 1 even if they also perform intrastate deliveries (App. 13a).
   - **Unreached contractual threshold issue:** As Footnote 8 of the opinion below notes (App. 6a n.8), Plaintiffs also argued that PAGA claims are excluded from the scope of the parties' arbitration agreement altogether—an independent state-law contract question the trial court and Court of Appeal did not reach.

4. **Complete Absence of Cert-Stage Amicus Support:**
   Although the Chamber of Commerce, Retail Litigation Center, and California Employment Law Council filed an amicus brief in the California Court of Appeal (App. 3a), **zero** amicus briefs were filed in support of Amazon's certiorari petition in this Court (`amicus_briefs: null` in `context.json`, and no amicus entries on `2026-11-06.json`, even though the original response due date was August 10, 2026). For a major corporate petitioner represented by Gibson Dunn seeking review of a recurring arbitration question, the absence of business-community amicus support at the cert stage is a strong negative signal.

---

## 4. Secondary Claims and Distribution Rationales

- **`relist-increment` (`0.98`):** The snapshot freezes `distribution_count: 1` (the August 12, 2026 distribution prior to the August 18, 2026 CFR). Because the BIO is due November 16, 2026, the petition will be distributed a second time once the BIO is filed (or the time expires), unless the case settles and is dismissed under Rule 46 in the interim (~2% chance).
- **`cvsg-increment` (`0.01`):** Practically zero chance of a CVSG on a private state-court FAA § 1 petition just months after *Brock*.
- **`summary-disposition-route` (`0.58`):** Conditional on a grant (`0.06`), a GVR in light of *Brock* (`0.035 / 0.060 ≈ 0.58`) is slightly more likely than plenary review (`0.025 / 0.060 ≈ 0.42`) because the opinion below pre-dated *Brock* and explicitly defined the worker class by reference to the pending *Brock* QP (App. 4a n.4, 8a–9a n.10).
- **`dissent-from-denial` (`0.02`) and `order-writers`:** Given the 9–0 consensus across *New Prime*, *Saxon*, *Bissonnette*, and *Brock*, a written dissent or statement respecting denial is unlikely (`0.02`), with small per-Justice probabilities assigned primarily to Justices Thomas (`0.008`), Alito (`0.006`), and Gorsuch (`0.003`).

---

## 5. Key Uncertainties

Because the snapshot (`2026-11-06.json`) precedes the November 16, 2026 due date for Respondents' Brief in Opposition, the BIO and Reply Brief do not yet exist. However, Respondents are represented by the same Counsel of Record (Jennifer Dale Bennett, Gupta Wessler LLP) who argued and won *Flowers Foods v. Brock* in May 2026, so the structure of the opposition—emphasizing *Brock*'s 9–0 affirmance, *Rittmann*'s settled treatment of Amazon Flex drivers, and the unpublished state-court posture—is highly predictable from the record below.
