# Predictor Reasoning — *Gengshu Scott He, et al. v. Marco Rubio, Secretary of State, et al.* (No. 26-405)

## Summary of Forecast

- **Predicted Disposition:** `denied` (`granted = 0`, `probability = 0.008`)
- **Confidence:** `0.92`
- **Big Case Score:** `0.15`

## 1. Base-Rate Anchoring (`metrics/statpack.md` and `record/context.json`)

This is a forward-mode cert-stage prediction at `moment: distribution` (`event_id: evt-petition-disposition`). From `record/context.json`, the conditioning state frozen at the `2026-10-31.json` snapshot is:
- `band`: `"baseline"` (`salience_version`: `"sal-v6"`)
- `distribution_count`: `1`
- `cvsg_date`: `null`
- `cert_anchor`: `rate = 0.0518752467429925` (~5.19%), pooled over `lookback_terms = 10` strictly prior to OT2026 (`statpack_digest: sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`).

In `metrics/statpack.md`, the relevant reference cuts for the modern discretionary-cert paid scored segment are:
- **Salience band (`baseline`, `sal-v6`):** The pooled `reached` rate across prior Terms is **5.19%** (ranging from 4.1% in OT2025, `n=1292`, to 6.1% in OT2023, `n=1284`). That `reached` denominator includes all private petitions that start in `baseline` at first distribution and later climb into `elevated` or `high` via a Call for Response, relist, amicus support, or CVSG. By contrast, the terminal `baseline` grant-family rate (petitions that remain in `baseline` through disposition) is **1.5%** (`0.9%` granted + `0.6%` GVR over `n=11,026` resolved).
- **Relist count (`relist_bucket = 0`):** Among paid scored-segment petitions with zero relists (`n=10,204` resolved), `96.8%` are denied, `1.3%` dismissed, `1.3%` granted, and `0.5%` GVR (**1.8%** grant family).
- **Amicus count (`cert_amicus = 0`):** Among paid scored-segment petitions with zero amicus briefs (`n=11,109` resolved), `95.0%` are denied, `2.0%` granted, `1.8%` GVR, and `1.3%` dismissed (**3.8%** grant family).
- **Originating court (`cadc`):** Across the denial-reweighted modern cert slice, D.C. Circuit petitions (`n=644` resolved) have a higher marginal grant-family rate (`6.1%` granted + `2.2%` GVR = **8.3%**), driven heavily by federal government petitions and high-salience administrative-law cases rather than private employment/FTCA disputes.

## 2. Case-Specific Adjustments from the Provisioned Record

Weighing the provisioned snapshot (`record/snapshots/2026-10-31.json`) and filings (`record/documents/petition.txt` and `record/documents/questions-presented.txt`) moves the forecast well below both the 5.19% `baseline` reached anchor and the ~1.5%–1.8% zero-relist terminal rate, down to **0.8% (`0.008`)**:

1. **Solicitor General Waiver of Response and Zero Amicus Support:**
   On October 16, 2026, Solicitor General D. John Sauer filed a waiver of the right of Respondents Marco Rubio and the United States to respond to the petition, and the petition was distributed on October 21, 2026 for the November 6, 2026 conference. No amicus briefs have been filed (`amicus_briefs: null` in `context.json`, zero entries on the docket). Without a Call for Response (CFR), the Court will not grant certiorari on a waived petition.
2. **Unpublished Motions-Panel Summary Affirmance Below:**
   Although the petition cites the D.C. Circuit's published opinion at 179 F.4th 8 (June 23, 2026, App. A, 1a–16a), that published merits opinion adjudicated *only* the common-law assault claim under Virginia law brought by Petitioner Gengshu He's family members—and the D.C. Circuit *reversed* the district court in the family's favor. Petitioner He's own FTCA claims (and the FECA preemption issue raised in the Question Presented) were disposed of 17 months earlier in a two-sentence paragraph of an **unpublished per curiam summary affirmance order** entered by a motions panel (Judges Millett, Wilkins, and Rao) on January 15, 2025 (App. B, 17a–19a). The Supreme Court rarely grants certiorari to review an unpublished summary affirmance that contains no substantive doctrinal analysis.
3. **Self-Inflicted Procedural Posture and Ongoing Remand:**
   In the district court (App. D, 32a–35a), Judge Friedrich did not initially dismiss He's FTCA claims (assault, battery, and false imprisonment); instead, she stayed Counts III–V so that He could seek a FECA coverage determination from the Secretary of Labor. Only after He filed a joint status report stating that he elected *not* to file a FECA claim did the district court lift the stay and dismiss his FTCA claims without prejudice (App. C, 20a–21a). Had He filed with the Office of Workers' Compensation Programs (OWCP) and had OWCP determined his injuries were not sustained in the performance of duty or were not compensable under FECA, he would have been free to proceed with his FTCA suit in district court (as the Ninth Circuit held in *Hawkins v. United States*, 14 F.4th 1018, 1021–22 (9th Cir. 2021)). Moreover, because the D.C. Circuit remanded the He family's FTCA claim arising from the same February 12, 2021 incident for further proceedings in the district court, the litigation as a whole remains interlocutory.
4. **Weakness of the Alleged Circuit Split as Applied to These Facts:**
   Petitioner contends (Pet. 1–2, 6–9) that the Ninth Circuit (*Moe v. United States*, 326 F.3d 1065 (9th Cir. 2003); *Figueroa v. United States*, 7 F.3d 1405 (9th Cir. 1993)) splits from ten other circuits (including *Daniels-Lumley v. United States*, 306 F.2d 769 (D.C. Cir. 1962), and *Fuqua v. United States Postal Service*, 956 F.3d 961 (7th Cir. 2020)) by holding that federal courts must independently determine whether an injury type falls within the "scope of FECA" without deferring to the Secretary of Labor. However:
   - Even in the Ninth Circuit, courts stay or dismiss FTCA actions when there is a "substantial question" whether an injury occurred in the performance of duty (*Reep v. United States*, 557 F.2d 204, 208 (9th Cir. 1977), cited in *Moe*, 326 F.3d at 1070 n.19, and cited by the district court here at App. 35a).
   - While Ninth Circuit precedent holds that purely emotional distress *divorced from any physical harm* is outside FECA's scope (*Sheehan v. United States*, 896 F.2d 1168, 1174 (9th Cir. 1990); *Moe*, 326 F.3d at 1068), Petitioner He expressly pleaded **battery** (alleging that Diplomatic Security Officer Peart physically grabbed his wrist across the threshold of his home while investigating alleged workplace misconduct, App. 24a–25a, 33a) in addition to assault and false imprisonment.
   - Most importantly, in this case the Department of Labor submitted a specific memorandum to the district court stating that "there is a substantial likelihood of coverage under ... FECA" for He's injuries "resulting from [the] alleged assault, battery, and false imprisonment at his home" (App. 33a). Thus, even a court examining FECA scope independently would confront an explicit representation by the administering agency that the claims fall within FECA's coverage perimeter.

## 3. Auxiliary Claims and Distributions (`cert-v3`)

- **`relist-increment` (`0.045`):** Because the Solicitor General waived a response, any Call for Response would require a subsequent distribution after the BIO is filed, and an administrative reschedule or conference relist would also increment `distribution_count` beyond 1. Given the vehicle flaws and short (10-page) petition, I place the probability of at least one additional distribution at 4.5%.
- **`cvsg-increment` (`0.001`):** The United States and the Secretary of State are the named Respondents represented by the Solicitor General. The Court does not invite the Solicitor General to file an amicus brief when the Solicitor General is already counsel for a party.
- **`summary-disposition-route` (`0.15`):** `record/same-question.json` shows `petitions: []` across 10,255 indexed petitions, and there is no pending Supreme Court case on FECA. Conditional on a grant, plenary review is far likelier (~85%) than a summary disposition in the cert order (~15%, which would essentially require a post-CFR confession of error or shift in position by the Solicitor General).
- **`dissent-from-denial` (`0.005`) and `order-writers`:** While the statutory argument that 5 U.S.C. §§ 8116(c) and 8128(b) do not strip federal courts of jurisdiction to determine threshold FECA coverage prior to an actual "action of the Secretary ... in allowing or denying a payment" has some textualist appeal, the vehicle defects make a separate statement on denial unlikely (~0.5%). In `order-writers`, small probabilities are assigned primarily to Justices Gorsuch (`0.002`) and Thomas (`0.002`), with `0.0005`–`0.001` for the remaining Justices.

## 4. Uncertainties and Limitations

The primary uncertainty is whether a single chambers views the sixty-year-old *Daniels-Lumley* "substantial question" rule as an improper judicial abdication of Article III jurisdiction under *Arbaugh v. Y&H Corp.*, 546 U.S. 500 (2006), sufficient to trigger a Call for Response despite the government's waiver. Even if a response were called for, however, the Brief in Opposition would highlight the unpublished summary affirmance below, the Department of Labor's case-specific memorandum finding a substantial likelihood of coverage, and Petitioner's refusal to pursue the administrative FECA determination during the district court's stay, almost certainly resulting in a denial.
