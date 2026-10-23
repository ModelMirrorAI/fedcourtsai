# Prediction Reasoning: *Novartis Pharmaceuticals Corporation v. Lynn Fitch, Attorney General of Mississippi* (`scotus/9026000457`)

## 1. Summary of Forecast Numbers

- **`granted`:** `0` (`predicted_disposition`: `"denied"`)
- **`probability` (`P(any grant)` / `disposition`):** `0.01`
- **`relist-increment`:** `0.06`
- **`cvsg-increment`:** `0.01`
- **`summary-disposition-route` (conditional on grant):** `0.35`
- **`dissent-from-denial` (conditional on denial):** `0.02`
- **`big_case_score`:** `0.65`

---

## 2. Case Overview and Provisioned Inputs

I read the provisioned snapshot `2026-10-22.json`, `record/context.json`, and all three provisioned document files under `record/documents/` (`questions-presented.txt`, `petition.txt`, and `appendix.txt`, listed in `documents.json` with `empty_text: false` and `truncated: false`).

Petitioner Novartis Pharmaceuticals Corporation seeks certiorari to review an unpublished per curiam judgment of the U.S. Court of Appeals for the Fifth Circuit (*Novartis Pharmaceuticals Corp. v. Fitch*, No. 24-60342, decided April 9, 2026; rehearing en banc denied May 5, 2026), which affirmed the Southern District of Mississippi's denial of a preliminary injunction against Mississippi House Bill 728 (`Miss. Code Ann. § 41-149-1` et seq.).

Mississippi's H.B. 728 prohibits pharmaceutical manufacturers from denying, restricting, or interfering with the acquisition of 340B-discounted drugs by, or delivery of such drugs to, outside "contract pharmacies" acting on behalf of covered entities under Section 340B of the Public Health Service Act (`42 U.S.C. § 256b`). In a 7-page unpublished per curiam opinion (`App. 1a-7a`), the Fifth Circuit panel (Judges Richman, Graves, and Ramirez) held that Novartis's Supremacy Clause field- and conflict-preemption challenges were foreclosed under the Fifth Circuit's rule of orderliness by *AbbVie, Inc. v. Fitch*, 152 F.4th 635 (5th Cir. 2025), and *AbbVie, Inc. v. Murrill*, 166 F.4th 528 (5th Cir. 2026).

### Docket Snapshot Signals (`2026-10-22.json` & `context.json`)
- **Mode / Stage / Moment:** `forward` / `cert` / `distribution` (`band: baseline`, `salience_version: sal-v4`)
- **Term:** `2026` (`Docket No. 26-457`, Paid petition docketed October 7, 2026)
- **Originating Court:** U.S. Court of Appeals for the Fifth Circuit (`ca5`)
- **Response Status:** Respondent Lynn Fitch filed a **Waiver of right to respond** on October 15, 2026. No response has been requested by the Court (`response_requested: null`).
- **Distribution Count:** `1` (Distributed on October 21, 2026, for the Conference of November 6, 2026).
- **CVSG Date / Amicus Briefs:** `cvsg_date: null`, `amicus_briefs: null` (zero cert-stage amicus briefs on the docket).

---

## 3. Base Rate Anchoring (`metrics/statpack.md`)

Following the cert-stage anchoring rules in `.github/prompts/predict.md`:

1. **Salience Band Anchor (`baseline` under `sal-v4`, strictly prior Terms OT2017–OT2025):**
   - `record/context.json` freezes `band: "baseline"` and `salience_version: "sal-v4"` in Term `2026`.
   - From the `Segment base rate by salience band (sal-v4)` table in `metrics/statpack.md`, pooling the bracketed `reached` figures across the 9 strictly prior Terms (`2017` through `2025`):
     - **2025:** `3.9%` (`n=1303`, ~50.8 grants)
     - **2024:** `5.7%` (`n=1271`, ~72.4 grants)
     - **2023:** `5.9%` (`n=1312`, ~77.4 grants)
     - **2022:** `5.8%` (`n=1192`, ~69.1 grants)
     - **2021:** `5.6%` (`n=1500`, ~84.0 grants)
     - **2020:** `4.5%` (`n=1739`, ~78.3 grants)
     - **2019:** `4.6%` (`n=1399`, ~64.4 grants)
     - **2018:** `4.6%` (`n=1524`, ~70.1 grants)
     - **2017:** `4.7%` (`n=1643`, ~77.2 grants)
   - Pooled across `n = 12,883` weighted resolved petitions in `baseline` (`reached`) over OT2017–OT2025, the weighted grant-family rate is approximately **5.00%** (`~643.7 / 12,883`).
   - By contrast, the leading figure for petitions that *ended* in `baseline` (0 relists, no CVSG, private petitioner) across OT2017–OT2025 is roughly **1.16%** (`0.6%` to `1.8%` across Terms; and `1.2%` overall in the `Cert petitions by salience band` table: `denied 97.6%, dismissed 1.2%, granted 0.8%, gvr 0.4%`).

2. **Signal Cuts (`metrics/statpack.md`):**
   - **Modern discretionary-cert petitions overall:** `denied` 42,529 (95.2%), `dismissed` 907 (2.0%), `granted` 662 (1.5%), `gvr` 588 (1.3%) (`resolved = 44,686`).
   - **Originating circuit (`ca5`):** `denied` 94.7%, `gvr` 2.1%, `granted` 1.6%, `dismissed` 1.6% (`resolved = 5,396`, grant family `3.7%`).
   - **Relist count (`0` relists, paid scored segment):** `denied` 97.0%, `granted` 1.2%, `dismissed` 1.2%, `gvr` 0.5% (`resolved = 10,169`, grant family `1.7%`).
   - **CVSG status (`none`, paid scored segment):** `denied` 92.7%, `granted` 3.9%, `gvr` 2.3%, `dismissed` 1.2% (`resolved = 13,494`).

---

## 4. Case-Specific Adjustments from the Anchor

Starting from the `baseline [reached]` anchor of **~5.0%**, several strong downward adjustments apply:

### A. Waiver of Response and Distribution Without a Call for Response (Strong Downward Adjustment)
The 5.0% `baseline [reached]` base rate pools all paid private-party petitions at first distribution—both those where the respondent filed a brief in opposition (or the Court called for a response prior to distribution) and those distributed on a waiver of response. Here, Respondent Lynn Fitch waived the right to respond on October 15, 2026, and the petition was distributed on October 21, 2026 for the November 6 conference without a Call for Response (`CFR`). Under modern Supreme Court practice, the Court virtually never grants certiorari straight off a waiver without requesting a response. To reach a grant from here, a Justice must first request a response at or before the November 6 conference, the BIO must be filed, the case must be redistributed/relisted, and four Justices must then vote to grant. Most waived petitions distributed without a CFR terminate at their first conference (`baseline` terminal grant-family rate of ~1.2%, and even lower conditional on a waiver).

### B. Complete Absence of a Circuit Split and Prior Cert Denial on the Same Issue (Strong Downward Adjustment)
As Novartis's petition itself reveals, **every federal court of appeals** to decide whether Section 340B preempts state laws prohibiting restrictions on contract-pharmacy deliveries has **upheld the state laws**:
- **Eighth Circuit:** Upheld Arkansas's Act 1103 in *Pharm. Rsch. & Mfrs. of Am. v. McClain*, 95 F.4th 1136 (8th Cir. 2024), *cert. denied*, 145 S. Ct. 768 (Dec. 9, 2024), and upheld Missouri's S.B. 751 in *Novartis Pharms. Corp. v. Hanaway*, 182 F.4th 573 (8th Cir. 2026).
- **Fifth Circuit:** Upheld Mississippi's H.B. 728 in *AbbVie, Inc. v. Fitch*, 152 F.4th 635 (5th Cir. 2025) (and in this case below), and upheld Louisiana's Act 358 in *AbbVie, Inc. v. Murrill*, 166 F.4th 528 (5th Cir. 2026).
- **Fourth Circuit:** Upheld West Virginia's S.B. 325 in *Pharm. Rsch. & Mfrs. of Am. v. McCuskey*, 175 F.4th 411 (4th Cir. 2026), and *Novartis Pharms. Corp. v. McCuskey*, 2026 WL 845920 (4th Cir. Mar. 31, 2026).

Not only is the circuit authority 3–0 against the manufacturers' preemption theory, but the Supreme Court already denied certiorari in *PhRMA v. McClain*, 145 S. Ct. 768 (2024), on the exact same question. While Novartis argues that the Third, Seventh, and D.C. Circuits (*Sanofi Aventis U.S. LLC v. HHS*, 58 F.4th 696 (3d Cir. 2023); *Novartis Pharms. Corp. v. Johnson*, 102 F.4th 452 (D.C. Cir. 2024); *Eli Lilly & Co. v. Becerra*, 158 F.4th 763 (7th Cir. 2025)) are in tension with the Fourth, Fifth, and Eighth Circuits, those decisions held only that *federal* law (Section 340B) is silent on delivery mechanics and therefore does not itself require unlimited contract-pharmacy deliveries. As the Fourth, Fifth, and Eighth Circuits all explained, federal statutory silence on delivery terms does not preempt state laws regulating pharmacy delivery within their borders.

### C. Weak Vehicle Characteristics (Moderate Downward Adjustment)
Even if four Justices wished to examine state 340B contract-pharmacy mandates despite the uniform circuit consensus, *Novartis v. Fitch* is a poor vehicle:
1. **Unpublished, derivative decision below:** The Fifth Circuit's 7-page unpublished per curiam opinion (`App. 1a-7a`) contains no independent doctrinal analysis; it merely holds that *AbbVie v. Fitch*, 152 F.4th 635 (5th Cir. 2025), is binding under the Fifth Circuit's rule of orderliness.
2. **Interlocutory posture and undeveloped factual record:** The appeal arises from the denial of a preliminary injunction (`738 F. Supp. 3d 737`). Notably, the United States' Fifth Circuit amicus brief in *Murrill*—which Novartis highlights repeatedly—argued that manufacturers' preemption challenges could not succeed on an abstract facial record and would require specific factual development regarding how individual contract-pharmacy models operate (`Inventory Replenishment` vs. standard purchase-and-title models). That undercuts certiorari in a pre-enforcement preliminary-injunction appeal.
3. **Zero cert-stage amicus briefs:** Although Petitioner is represented by experienced Supreme Court counsel (Jessica L. Ellsworth), no amicus briefs were filed supporting certiorari prior to conference distribution.

---

## 5. Calibration of Declared Claims and Big-Case Score

- **`disposition` (`0.01`) & `predicted_disposition` (`"denied"`):** Balancing the 5.0% `baseline [reached]` anchor against the waiver of response without a CFR, the 0–3 uniform circuit landscape against preemption, the prior cert denial in *McClain*, the interlocutory preliminary-injunction posture, the unpublished derivative Fifth Circuit opinion, and the lack of cert-stage amicus support yields `P(grant) = 0.01` (`granted = 0`, `predicted_disposition = "denied"`).
- **`relist-increment` (`0.06`):** Because the petition was distributed on a waiver without a CFR, it will only be redistributed/relisted if a Justice calls for a response at the November 6 conference or holds the petition. Given the lack of a circuit split and the derivative unpublished opinion below, I estimate a `0.06` probability of a CFR/hold leading to at least one additional distribution beyond `distribution_count = 1`.
- **`cvsg-increment` (`0.01`):** Across the paid scored segment, only ~1.3% (`179 / 14,093`) of petitions ever receive a CVSG. Here, no response has been requested from the state, the United States already stated its position on state contract-pharmacy preemption in its Fifth Circuit amicus brief in *Murrill*, and this is an unpublished interlocutory vehicle. Thus `P(cvsg-increment) = 0.01`.
- **`summary-disposition-route` (`0.35`):** Across the modern discretionary-cert population in `metrics/statpack.md`, GVRs account for roughly 47% of the grant family (`588 / (662 + 588)`), and ~37% in the paid scored segment (`none` CVSG cut: `2.3% / (3.9% + 2.3%)`). Conditional on the unlikely event that the Court grants review here, I set `P(summary-disposition-route | grant) = 0.35`, reflecting the possibility of a GVR if the Court were to hold the petition for another 340B case or remand for consideration of the as-applied framework discussed by the United States, while recognizing that a plenary grant to address the 20-state statutory wave would be the primary motivation for reaching the issue (`0.65`).
- **`dissent-from-denial` (`0.02`):** Conditional on denial, a separate dissent or statement respecting denial is unlikely (`0.02`), as the Court previously denied certiorari in *PhRMA v. McClain* without noted dissent and there is no circuit split.
- **`big_case_score` (`0.65`):** Decoupled from grant likelihood, the underlying legal question—whether states may require pharmaceutical manufacturers to deliver 340B-discounted drugs to an unlimited number of for-profit contract pharmacies—is of substantial commercial and public-policy significance (`$66.3 billion` in annual 340B purchases and legislation in roughly 20 states).

---

## 6. Key Uncertainties

The primary source of residual uncertainty is whether another Section 340B contract-pharmacy petition (such as a petition from the Fourth Circuit's *McCuskey* decisions or the Eighth Circuit's *Hanaway* decision) draws a Call for Response or grant later in OT2026, which could prompt the Court to call for a response and hold *Novartis v. Fitch* pending that matter. However, because respondent waived and no CFR has issued ahead of the November 6 conference, the overwhelming likelihood is a clean denial at first conference.
