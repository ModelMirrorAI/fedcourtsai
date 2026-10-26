# Predictor Rationale: *Diana Y. Lugo v. Birmingham Jefferson County Transit Authority* (No. 26-545)

## 1. Summary of Forecast

- **Headline Probability (`probability` / `disposition`):** `0.002` (`granted: 0`, `predicted_disposition: "denied"`)
- **Conditioning State:** `mode: forward`, `stage: cert`, `moment: arrival`, `band: baseline` (`salience_version: sal-v4`), `distribution_count: 0`, `cvsg_date: null`, `term: 2026`
- **Input Snapshot Read:** `2026-10-27.json` (plus provisioned filings `questions-presented.txt`, `petition.txt`, `appendix.txt`, and metadata in `documents.json`)

## 2. Base-Rate Anchoring (`metrics/statpack.md`)

This cell forecasts `evt-petition-arrival-disposition` (`moment: arrival`) for a paid cert petition (`CaseNumber: "26-545"`, `sJsonCaseType: "Paid"`) filed by a private petitioner (`band: baseline` under `sal-v4`).

1. **Salience Band Arrival Anchor (`sal-v4`, `baseline`):**
   Per the cert-stage arrival anchoring rule, we anchor on the `baseline` band's bracketed `reached` rate pooled across all statpack Terms strictly preceding OT2026 (OT2017–OT2025, 9 Terms):
   - OT2025: 4.0% (n=1,313)
   - OT2024: 5.9% (n=1,274)
   - OT2023: 5.9% (n=1,312)
   - OT2022: 5.9% (n=1,196)
   - OT2021: 5.7% (n=1,500)
   - OT2020: 4.5% (n=1,740)
   - OT2019: 4.7% (n=1,399)
   - OT2018: 4.8% (n=1,529)
   - OT2017: 4.9% (n=1,649)
   Pooling across all 12,912 resolved petitions that reached the `baseline` band in OT2017–OT2025 yields approximately 659.4 grants (`granted` + `gvr`), or a pooled `reached` base rate of **5.11%** (5.1%). (By contrast, petitions that *ended* in `baseline` without ever relisting or drawing a CVSG granted at **1.30%** across n=9,773.)
2. **Whole-Docket and Circuit Cuts:**
   - Across all modern discretionary-cert petitions (paid + IFP, denial-reweighted, n=44,786 resolved), the overall grant-family rate is **2.85%** (1.5% `granted`, 1.3% `gvr`, 95.1% `denied`, 2.0% `dismissed`).
   - For the originating circuit (`ca11`, Eleventh Circuit, n=3,692 resolved in the modern reweighted cut), the grant-family rate is **3.6%** (1.7% `granted`, 1.9% `gvr`, 94.6% `denied`, 1.9% `dismissed`).

## 3. Case-Specific Adjustments from the Provisioned Record

Starting from the **5.11%** `baseline` reached anchor for paid private petitions, several strong negative features in the provisioned snapshot (`2026-10-27.json`) and filings (`questions-presented.txt`, `petition.txt`, `appendix.txt`) warrant a steep downward adjustment to **0.2% (`0.002`)**:

1. **Pro Se Representation on the Paid Docket:**
   Although docketed in the `26-` paid series rather than the `26-5xxx` IFP series, the snapshot (`"IsCounselofRecord": false`, `"Party": "Diana Y. Lugo"`, `"Attorney": "Diana Y. Lugo"`) and `petition.txt` confirm that Petitioner Diana Y. Lugo is litigating **pro se**. Empirically, pro se petitions filed on the paid docket without Supreme Court bar counsel have grant rates approximating the IFP docket (~0.1%–0.3%) rather than represented paid petitions. Furthermore, `petition.txt` exhibits severe drafting defects, including fabricated or garbled citations (e.g., citing `"Reeves v. Kerner, 404 U.S. 519 (1972)"` at Pet. 14—conflating *Haines v. Kerner*, 404 U.S. 519 (1972), with *Reeves v. Sanderson Plumbing Products, Inc.*, 530 U.S. 133 (2000)) and unedited AI-assistant coaching text pasted directly into the body of the argument (Pet. 10: *"To frame this argument successfully in your petition, you must ground it in established Supreme Court rulings... Rather than merely asking if a reasonable jury could find in your favor, the judge effectively held a bench trial on paper and stripped you of your right to a jury."*).
2. **Unpublished, Non-Argument Calendar Per Curiam Decision Below:**
   As `appendix.txt` (App. 4(a)–14(a)) shows, the Eleventh Circuit's June 8, 2026 opinion (No. 25-11476, per curiam before Judges Newsom, Grant, and Brasher) was designated `NOT FOR PUBLICATION` on the `Non-Argument Calendar`. It sets no circuit precedent, and rehearing en banc was denied on July 27, 2026 without any active judge requesting a poll (App. 2(a)–3(a)).
3. **Severe Vehicle Defects Across All Three Questions Presented:**
   - **QP 1 (Title VII Comparator Standard):** Petitioner argues that the Eleventh Circuit's en banc standard in *Lewis v. City of Union City*, 918 F.3d 1213 (11th Cir. 2019) (requiring a comparator to be "similarly situated in all material respects"), conflicts with *McDonnell Douglas* and other circuits. However, the Eleventh Circuit panel explicitly noted at the outset of its Title VII discussion (App. 9(a)) that a plaintiff may defeat summary judgment using "a wide variety of circumstantial evidence—whatever 'would allow a jury to infer intentional discrimination by the decisionmaker'" (quoting *Tynes v. Fla. Dep't of Juv. Just.*, 88 F.4th 939, 946 (11th Cir. 2023), and citing *Ismael v. Roundtree*, 161 F.4th 752, 760 (11th Cir. 2025)). The panel addressed comparator evidence only because Lugo herself argued that coworkers received more favorable treatment, and her primary comparator for the August 2020 promotion (Alicia Pebbles) undisputedly had longer tenure, while Pebbles was *also* written up and ordered back to the office for remote-work login/logout issues (App. 9(a)–10(a) & n.1). Moreover, at the pretext stage, Lugo had an extensive documented disciplinary history—scheduling paratransit rides for disabled passengers at 4:00 a.m. instead of 4:00 p.m., hanging up on a customer, and failing her performance improvement plan—with no evidence of racial or national-origin animus (App. 5(a)–6(a), 10(a)–11(a)).
   - **QP 2 (Rule 56 Summary Judgment / Seventh Amendment / Pro Se Liberal Construction):** This is pure fact-bound error correction. Contrary to Petitioner's assertion that the Eleventh Circuit repudiated liberal construction of pro se filings, the panel explicitly forgave her overlength 50-page opening brief and 30-page reply brief ("giving Lugo the absolute benefit of the doubt, we will proceed to the merits of her appeal," App. 8(a)), and Judge Axon in the district court likewise liberally construed her filings under *Erickson v. Pardus*, 551 U.S. 89, 94 (2007) (App. 19(a)–20(a)).
   - **QP 3 (Third-Party ADA Retaliation under 42 U.S.C. § 12203(a)):** Although Petitioner claims an entrenched circuit split over whether advocating for disabled customers constitutes protected activity under the ADA's opposition clause, **the Eleventh Circuit explicitly declined to decide that question**, holding instead that causation failed on temporal proximity: *"Setting aside lingering uncertainties as to what Lugo actually did and whether that conduct would be protected under the ADA, the temporal proximity between Lugo's September 2019 conduct and the challenged employment actions is not proximate at all. Again, the earliest of the allegedly retaliatory actions occurred almost a year later"* (App. 13(a)–14(a)). That independent, fact-bound causation holding renders this case an impossible vehicle to reach QP 3.

## 4. Secondary Claims and Authorship Distributions

- **`relist-increment` (`0.98`):** Under the harness resolver (`outcome.signals.distribution_count > context.distribution_count`), because `context.distribution_count` is `0` at `moment: arrival`, this claim resolves to `1` as soon as the petition is distributed for its first conference (`distribution_count >= 1`). In the statpack's modern cert table, only ~2.0% of petitions are dismissed (and ~1.3% in the paid scored segment's `relist_bucket = 0`), most of which are settled commercial disputes under Rule 46. A pro se petitioner who just paid the docketing fee is very unlikely to settle or withdraw prior to initial conference distribution, so we set `relist-increment` at **0.98**. (As noted in `predicted_reasoning.md`, the probability of a true conference relist *beyond* the initial distribution—i.e., `distribution_count >= 2`—is ~0.015–0.02.)
- **`cvsg-increment` (`0.001`):** In the paid scored segment, CVSGs occur in only 164 of 13,718 resolved petitions (1.20%), and virtually never in fact-bound pro se municipal employment appeals.
- **`summary-disposition-route` (`0.35`):** Conditional on a grant, the statpack's paid scored segment shows a GVR share of roughly 36% of grants (`5.5% / 34.8%` in CVSG, `5.2% / 13.7%` in relist-1, `0.5% / 1.8%` in relist-0). Conditional on the remote event of a grant here, a GVR following an intervening Title VII decision is roughly 35% vs. 65% plenary review.
- **`dissent-from-denial` (`0.002`) and `order-writers`:** Given the unpublished opinion below, the alternative causation ground on QP 3, and the pro se drafting issues, a separate statement or dissent from denial is around 0.2%, distributed across the nine sitting Justices (`Roberts: 0.0001`, `Thomas: 0.0005`, `Alito: 0.0003`, `Sotomayor: 0.0005`, `Kagan: 0.0001`, `Gorsuch: 0.0005`, `Kavanaugh: 0.0002`, `Barrett: 0.0001`, `Jackson: 0.0005`).
- **`big_case_score` (`0.03`):** Routine individual employment termination dispute with no broader public, institutional, or doctrinal salience.

## 5. Uncertainties and Discounting Notes

- Both `petition.txt` and `appendix.txt` carry `"ocr_derived": true` and `"contact_scrubbed": true` in `documents.json` (`questions-presented.txt` is extracted from `petition.txt`). All case citations and lower-court holdings relied upon in this rationale were cross-checked directly against the Eleventh Circuit's opinion and the Northern District of Alabama's orders reproduced in `appendix.txt`.
- At `moment: arrival`, no Brief in Opposition (`brief-in-opposition.txt`) has been filed yet; our assessment of Respondent's arguments is inferred from the Eleventh Circuit and District Court opinions in `appendix.txt`.
