# Rationale for Prediction: *Christopher Rydberg v. United States*, No. 26-441

## I. Summary of Numbers

- **`granted`**: `0` (`predicted_disposition`: `"denied"`)
- **`probability` / `claims[disposition]`**: `0.008` (0.8% chance of grant; 99.2% chance of denial)
- **`claims[relist-increment]`**: `0.035`
- **`claims[cvsg-increment]`**: `0.001`
- **`claims[summary-disposition-route]`**: `0.15`
- **`claims[dissent-from-denial]`**: `0.012`
- **`big_case_score`**: `0.15`

---

## II. Provisioned Inputs and Anchor Base Rates

### 1. Provisioned Record Read
I read the provisioned snapshot `record/snapshots/2026-11-07.json`, `record/context.json`, `record/same-question.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, and the full text of `record/documents/petition.txt` (including the unpublished Fifth Circuit opinion in Appendix A and the rehearing denial in Appendix B). Neither `decision-below.txt` nor `lower-court-docket.txt` was separately staged in `record/documents/`, as the Fifth Circuit's opinion and rehearing order are reproduced in full inside `petition.txt`.

### 2. Statpack Anchor and Conditioning Cuts
From `record/context.json`, this cell is in `forward` mode at `moment: distribution` (`cutoff: null`), with `band: "baseline"`, `salience_version: "sal-v7"`, `distribution_count: 1`, `cvsg_date: null`, `amicus_briefs: null`, and `term: 2026`.
- **Frozen `cert_anchor`:** `context.json` provides `cert_anchor.rate = 0.051512996760685784` (~5.15%), pooled over the `lookback_terms: 10` window prior to OT2026 from `metrics/statpack.json` (`statpack_digest: sha256:12982c9a25e7998d76e1aafb22b3ca0657ce795865da1de43d69d124df555fb0`). In `metrics/statpack.md` ("Segment base rate by salience band (sal-v7)"), the bracketed `[reached]` rates for the `baseline` band across the nine rendered prior Terms (OT2017–OT2025) range from 4.0% (OT2025, `n=1289`) to 6.0% (OT2023, `n=1283`; OT2024, `n=1243`), while the terminal `baseline` rate (petitions that *end* in `baseline` without ever relisting or drawing a CVSG) is 0.7%–1.9% across OT2017–OT2025 (and 1.4% overall in "Cert petitions by salience band": `granted 0.8%, gvr 0.6%` over `n=11020` resolved).
- **Relist Cut:** In "Cert petitions by relist count (paid scored segment)", petitions ending in `relist_bucket = 0` (`n=10204` resolved) have a base rate of `denied 96.8%, dismissed 1.3%, granted 1.3%, gvr 0.5%` (1.8% grant family), whereas `relist_bucket = 1` (`n=2532`) jumps to `granted 8.3%, gvr 5.2%` (13.5% grant family).
- **Amicus Cut:** In "Cert petitions by amicus-brief count (paid scored segment)", `cert_amicus = 0` (`n=11109` resolved) grants at 3.8% (`granted 2.0%, gvr 1.8%`), compared to 14.8% for `1` (`n=1158`) and 22.7% for `2+` (`n=1446`).
- **Originating Circuit Cut:** In "Modern cert petitions by originating circuit", Fifth Circuit (`ca5`) petitions (`n=5456` resolved) resolve as `denied 94.7%, gvr 2.2%, dismissed 1.6%, granted 1.5%` (3.7% grant family).

---

## III. Adjustments from the 5.15% Anchor to `P(grant) = 0.008`

Starting from the 5.15% `baseline` risk-set anchor (`cert_anchor.rate`), several case-specific factors drive a substantial downward adjustment to **0.8%** (`0.008`):

1. **Solicitor General Waiver and Distribution Without a Call for a Response:**
   The petition was docketed on October 2, 2026. On October 29, 2026, Solicitor General D. John Sauer filed a waiver of the right of respondent United States to respond. On November 4, 2026, the petition was distributed for the Conference of December 4, 2026 (`distribution_count: 1`), with no call for a response (`response_requested: null`) and no *amicus* briefs filed. While the 5.15% `baseline` risk-set rate pools all private paid petitions at their first distribution (including petitions where the respondent filed a brief in opposition or where strong *amici* and circuit splits prompt a CFR/relist), a criminal defendant's paid petition in which the Solicitor General has waived a response and no amicus brief has been filed faces a much lower hazard of drawing a CFR and eventual grant.

2. **Complete Absence of a Circuit Split (QP I):**
   Petitioner was convicted in the Northern District of Texas of conspiring to commit health care fraud (18 U.S.C. §§ 1349, 1347), money laundering (18 U.S.C. § 1956(h), (a)(1)(B)(i)), and tax fraud (18 U.S.C. § 371) arising out of a compounding-pharmacy kickback scheme that billed the Department of Labor's Office of Workers' Compensation Programs (DOL-OWCP) under the Federal Employees' Compensation Act (FECA) for over $90.9 million and Blue Cross Blue Shield (BCBS) for $465,033. Petitioner contends in QP I that FECA is a statutory workers' compensation program rather than a health insurance "plan" or "contract" under 18 U.S.C. § 24(b) ("any public or private plan or contract, affecting commerce, under which any medical benefit, item, or service is provided to any individual"), contrasting § 24(b) with 42 U.S.C. § 1320a-7b(f)(1) ("any plan or program that provides health benefits, whether directly, through insurance, or otherwise").
   Critically, however, **no federal court of appeals or district court has ever agreed with petitioner's reading**. The Fifth Circuit (*United States v. Shah*, 95 F.4th 328, 359–60 (5th Cir. 2024); *United States v. Anderson*, 980 F.3d 423, 428 (5th Cir. 2020); *United States v. Collins*, 774 F.3d 256, 260 (5th Cir. 2014)) and other circuits (*e.g.*, *United States v. Lucien*, 347 F.3d 45, 52 (2d Cir. 2003); *United States v. Gelin*, 712 F.3d 612 (1st Cir. 2013)) uniformly treat public and private medical-reimbursement programs for injured workers or motorists as covered by § 24(b). Furthermore, as a matter of ordinary statutory meaning, FECA's medical-benefit program (5 U.S.C. § 8103(a)), under which DOL-OWCP adjudicates and pays medical and pharmacy bills for injured federal employees, comfortably qualifies as a "public ... plan ... under which any medical benefit, item, or service is provided to any individual."

3. **Unpublished Per Curiam Opinion and Fact-Bound Vehicle Obstacles (QP II & QP III):**
   - The Fifth Circuit decided this appeal in a short, unpublished *per curiam* opinion (`No. 25-10365`, 2026 WL 1683484; Pet. App. 1a–14a) that creates no circuit precedent.
   - QP II attacks a single word in *United States v. Anderson*, 980 F.3d 423, 428 (5th Cir. 2020)—noting that courts interpret § 24(b) "broadly"—which merely described Congress's use of the expansive modifier "any" three times in § 24(b).
   - QP III asks the Court to resolve the abstract debate over the rule of lenity's ambiguity threshold (*Wooden v. United States*, 595 U.S. 360 (2022)). The Court will not take up a foundational question of criminal statutory interpretation in a splitless case where the statute is not grievously (or even genuinely) ambiguous.
   - **Alternative BCBS Ground:** Count 1 charged a dual-object conspiracy to defraud both FECA and BCBS, and petitioner concedes BCBS is a "health care benefit program" under § 24(b). The Fifth Circuit expressly held that sufficient evidence supported the jury's finding that petitioner conspired to defraud both FECA and BCBS (Pet. App. 3a). While petitioner argues that a general verdict tainted by a legally invalid object requires harmless-error review under *Hedgpeth v. Pulido*, 555 U.S. 57 (2008), and *Neder v. United States*, 527 U.S. 1 (1999), and that his money-laundering convictions (Counts 10–16) and sentencing loss calculation depended on FECA proceeds, that dispute makes this a messy, record-intensive vehicle at the threshold.

4. **Upward Counter-Considerations (Why `P(grant)` Is 0.008 Rather Than <0.002):**
   Petitioner is represented by experienced Supreme Court and appellate practitioner Brent E. Newton, and the petition is well-written, highlighting an interesting textual contrast between two definitions enacted on the same day in HIPAA (18 U.S.C. § 24(b) vs. 42 U.S.C. § 1320a-7b(f)(1)) and pitching QP III directly to Justice Gorsuch's and Justice Sotomayor's lenity concurrence in *Wooden*. There is a small (~3.5%) chance a chambers flags the petition for a CFR, and conditional on a CFR/relist, a ~20–25% chance of an eventual grant, yielding `0.008` overall.

---

## IV. Secondary Claims and Distribution Rationale

- **`relist-increment` (`0.035`):** Reflects the ~3.5% probability that a Justice calls for a response from the Solicitor General (which would result in a subsequent distribution once the BIO is filed) or that the case is rescheduled/relisted for administrative reasons.
- **`cvsg-increment` (`0.001`):** Near zero because the United States is the respondent.
- **`summary-disposition-route` (`0.15`):** Conditional on a grant, there is no companion or lead case (`same-question.json` is empty) to trigger a routine GVR, so plenary review would be the primary route (~85%), with a 15% conditional share for a GVR or summary disposition if the Solicitor General's called-for response were to concede a partial error or remand issue.
- **`dissent-from-denial` (`0.012`) & `order-writers`:** Given the rule-of-lenity pitch in QP III citing Justice Gorsuch's concurrence in *Wooden* (joined by Justice Sotomayor) and Justice Thomas's skepticism of broad federal fraud theories, I assign `0.012` to the probability of a dissent or statement respecting denial, concentrated primarily on `Gorsuch` (`0.006`), `Thomas` (`0.003`), `Sotomayor` (`0.002`), and `Jackson` (`0.0015`).
- **`big_case_score` (`0.15`):** While a ruling excluding FECA from 18 U.S.C. § 24(b) would affect federal workers'-compensation pharmacy fraud prosecutions, the case involves a narrow statutory definition, an unpublished lower-court opinion, no circuit conflict, and no broader constitutional or institutional salience.

---

## V. Uncertainty and Retrieval Note

During retrieval, two initial CourtListener MCP opinion searches ran before the upstream CourtListener API returned `HTTP 429` rate-limit responses on two follow-up calls; as instructed by the prompt contract, I relied on the provisioned record (which already contains the full petition, appendix opinion, and statutory citations) and the local `fedcourts query` corpus tool and `metrics/statpack.md`. No material information was missing.
