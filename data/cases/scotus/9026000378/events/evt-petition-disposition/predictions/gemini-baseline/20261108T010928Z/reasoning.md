# Predictor Rationale — *Charles Kakembo Sessanga v. City of DeSoto Police Department, et al.* (No. 26-378)

## Summary of Call

- **Predicted disposition:** `denied` (`granted = 0`)
- **`probability` (P(grant)):** `0.005` (0.5%)
- **`big_case_score`:** `0.03`

## Base-Rate Anchoring

From `record/context.json` and `metrics/statpack.md`:

1. **Salience-band anchor (`sal-v8`):** `record/context.json` freezes `band: "baseline"` under `salience_version: "sal-v8"` for `term: 2026`, with `cert_anchor.rate = 0.051512996760685784` (~5.15%) pooled over the `lookback_terms: 10` strictly prior Terms (`statpack_digest: sha256:b122cc43052b1328321031e3615601101a1b85c7dcdc87d23e5436373b03f133`). In `metrics/statpack.md` ("Segment base rate by salience band (sal-v8)"), the bracketed `reached` grant-family rates for `baseline` across OT2017–OT2025 range from 4.0% (OT2025, n=1289) to 6.0% (OT2023, n=1283; OT2024, n=1243).
2. **Signal cuts in `metrics/statpack.md`:**
   - **Relist count (paid scored segment):** At `relist_bucket = 0` (1 distribution, 0 relists, n=10,204 resolved), the base rate is 96.8% denied, 1.3% granted, 0.5% GVR, 1.3% dismissed (1.8% grant-family rate).
   - **CVSG status (paid scored segment):** For `cvsg = none` (n=13,549 resolved), the base rate is 92.4% denied, 4.1% granted, 2.3% GVR, 1.2% dismissed.
   - **Amicus-brief count (paid scored segment):** For `cert_amicus = 0` (n=11,109 resolved), the base rate is 95.0% denied, 2.0% granted, 1.8% GVR, 1.3% dismissed.
   - **Originating circuit:** For `ca5` in "Modern cert petitions by originating circuit" (n=5,464 resolved), the base rate is 94.7% denied, 1.5% granted, 2.2% GVR, 1.6% dismissed (3.7% grant-family rate).
   - **Terminal `baseline` band:** Petitions that remain in `baseline` at disposition (n=11,020 resolved) resolve at 97.3% denied, 0.8% granted, 0.6% GVR, 1.3% dismissed (1.4% grant-family rate).

## Case-Specific Adjustments from the Provisioned Record

Starting from the 5.15% `baseline` risk-set anchor (`cert_anchor.rate`), I adjust sharply downward to **0.5% (`0.005`)** based on the provisioned snapshot (`record/snapshots/2026-11-08.json`) and filed documents (`record/documents/questions-presented.txt`, `record/documents/petition.txt`, and `record/documents/appendix.txt`):

1. **Pro se posture and unopposed distribution:** Although docketed on the paid docket (`sJsonCaseType: "Paid"`), Petitioner Charles Kakembo Sessanga is proceeding *pro se* (after proceeding *in forma pauperis* in the district court, App. 3, 15). Because the district court dismissed the action *sua sponte* prior to service under 28 U.S.C. § 1915(e)(2)(B)(ii), none of the respondents ever appeared below, and no respondent filed a brief in opposition or waiver by the October 21, 2026 response due date. The petition was distributed on November 4, 2026 for the December 4, 2026 conference (`distribution_count: 1`) without a response or a call for a response (CFR). Pro se petitions distributed without a response or amicus support are denied at a rate exceeding 99%. (Note: the snapshot lists `"Date": "Feb 06 2026"` on the initial petition filing entry corresponding to the Clerk's February 6, 2026 received stamp on the petition cover, before formal docketing on September 21, 2026.)
2. **Unpublished, fact-bound decision below (`appendix.txt`, App. 1–6, 15–26):** The Fifth Circuit's three-judge per curiam opinion (*Sessanga v. City of DeSoto Police Department*, No. 24-11050, Oct. 8, 2025, App. 1–6) is unpublished under 5th Cir. R. 47.5 and creates no circuit precedent. It affirms the adoption of Magistrate Judge David L. Horan's Findings, Conclusions, and Recommendation (App. 15–24) by Senior District Judge A. Joe Fish (App. 25–26).
3. **Lack of a genuine circuit conflict or legal error:**
   - **Question Presented 1 & Argument V (28 U.S.C. § 1915(e)(2) screening):** Petitioner argues that pre-service dismissal for failure to state a claim conflicts with *Neitzke v. Williams*, 490 U.S. 319 (1989), and *Leatherman v. Tarrant County*, 507 U.S. 163 (1993). However, *Neitzke* construed former 28 U.S.C. § 1915(d) prior to the Prison Litigation Reform Act of 1996 (PLRA), which enacted 28 U.S.C. § 1915(e)(2)(B)(ii) and expressly mandated dismissal "at any time" if the complaint "fails to state a claim on which relief may be granted." Every court of appeals applies the *Twombly*/*Iqbal* Rule 12(b)(6) plausibility standard to § 1915(e)(2)(B)(ii) dismissals.
   - **Question Presented 2 (Independent-intermediary doctrine):** Petitioner asserts a split with the Second (*Garnett v. Undercover Officer C0039*, 838 F.3d 265 (2d Cir. 2016)), Seventh (*Manuel v. City of Joliet*, 903 F.3d 667 (7th Cir. 2018)), and Ninth (*Awabdy v. City of Adelanto*, 368 F.3d 1062 (9th Cir. 2004)) Circuits. Yet the Fifth Circuit's opinion explicitly states the same rule—that "[o]n a motion to dismiss, mere allegations of taint can suffice if the inference of taint is supported by other facts alleged" (*McLin v. Ard*, 866 F.3d 682, 689–90 (5th Cir. 2017), cited at App. 4). The Fifth Circuit simply concluded that Petitioner's complaint—even after an amendment and written objections to the magistrate judge's report—alleged only that he and his wife voluntarily brought text messages and video to the detective and that the detective continued the investigation anyway (App. 2, 5). Moreover, the magistrate judge identified an independent ground for dismissal: the child victim's outcry itself furnished probable cause (App. 19–20), and the prosecutor was shielded by absolute immunity under *Imbler v. Pachtman*, 424 U.S. 409 (1976), for initiating the prosecution and cross-examining Petitioner's wife at trial (App. 5, 21–22).
   - **Question Presented 3 (Misdemeanor plea offer as evidence of lack of probable cause):** Neither the Fifth Circuit opinion nor the district court orders addressed this argument, making this case a poor vehicle to reach it even if the contention had any doctrinal support.

## Incremental and Conditional Claims

- **`relist-increment` (`0.015`):** Because no response was filed, the Court would have to issue a CFR (which triggers a subsequent distribution once the BIO arrives) before granting review. Given the clear vehicle and merits defects, the probability of a CFR or relist is very low (~1.5%).
- **`cvsg-increment` (`0.001`):** Practically zero in a pro se § 1983 suit against local Texas police officers and a county prosecutor.
- **`summary-disposition-route` (`0.35`):** Conditional on a grant, roughly 35% of the probability mass lies on a summary vacatur/remand (GVR or per curiam remand on pro se pleading standards) versus 65% on plenary review.
- **`dissent-from-denial` (`0.002`) and `order-writers`:** Separate writings on routine pro se § 1983 cert denials are exceedingly rare; small per-Justice probabilities (`0.0001` to `0.0008`) reflect the tiny baseline chance of a statement or dissent respecting denial.

## Uncertainties and Limitations

- Lower-court opinion and docket files (`decision-below.txt` and `lower-court-docket.txt`) were not separately staged in `record/documents/`, as `documents.json` contains `petition.txt`, `appendix.txt`, and `questions-presented.txt`. However, `appendix.txt` reproduces the complete Fifth Circuit opinion, judgment, rehearing denial order, and Northern District of Texas magistrate judge FCR and district court adoption order (App. 1–27), leaving no material gap in the record below.
