# Predictor Rationale (`scotus/9026000602`, `evt-petition-arrival-disposition`)

## 1. Summary of Forecast

- **Prediction:** `denied` (`granted = 0`, `probability = 0.002`)
- **Moment & Mode:** `arrival` (`evt-petition-arrival-disposition`), `forward` mode
- **Input Snapshot:** `2026-11-10.json` (docketed November 9, 2026; linked with extension application `25A442`)
- **Provisioned Documents Consulted:** `questions-presented.txt`, `petition.txt` (49 pages), `appendix.txt` (224 pages, truncated at the 150,000-character pipeline cap with inline `[pipeline note: ...]` markers), and `documents.json`.

## 2. Base-Rate Anchoring

From `record/context.json`, the cell's frozen conditioning state is:
- `band`: `"baseline"` under `salience_version`: `"sal-v8"`
- `term`: `2026`
- `distribution_count`: `0`, `cvsg_date`: `null`, `amicus_briefs`: `0`
- `cert_anchor`: `rate = 0.051587928582714486` (~5.16%), pooled over `lookback_terms = 10` (`OT2016`–`OT2025`) from `metrics/statpack.json` (`sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`).

In `metrics/statpack.md`:
- Across the 10 prior Terms (`OT2016`–`OT2025`) in the **"Segment base rate by salience band (`sal-v8`)"** table, the `baseline` band's bracketed `[reached]` rate—the arrival base rate for private paid petitions—ranges from `4.0%` (`OT2024`, `n=943`) to `6.0%` (`OT2022`, `n=983`), pooling to the `5.16%` `cert_anchor.rate`.
- In the **"Modern discretionary-cert petitions by disposition"** table (`n = 113,189`), the overall modern cert rate is `95.3%` denied, `3.2%` dismissed, `1.1%` granted, and `0.4%` GVR (`1.5%` grant family).
- By originating court (**"Cert petitions by originating circuit"**), petitions from the Florida District Courts of Appeal and Supreme Court of Florida grant at well under `1.0%` (e.g., Supreme Court of Florida: `97.0%` denied, `2.8%` dismissed, `0.2%` GVR, `n = 1,750`; Fourth DCA: `95.1%` denied, `4.3%` dismissed, `0.6%` granted, `n = 344`; First DCA: `95.8%` denied, `4.2%` dismissed, `0.0%` granted, `n = 285`).

## 3. Case-Specific Adjustments (Downward from `5.16%` to `0.2%`)

Several strong case-specific factors drive the probability of certiorari down from the `5.16%` private-arrival `baseline` anchor to `0.002` (`0.2%`):

1. **Pro Se Litigants on the Paid Docket:**
   - Although docketed as a paid case (`26-602`), petitioners Palanikumar V. Gnanam and Mullairani Gnanam are proceeding *pro se* (and state in `petition.txt` that they have proceeded *pro se* at every level of the litigation). Paid *pro se* petitions seeking review of state small-claims or county-court judgments have an empirical grant rate near zero.

2. **Fundamental Misapplication of Federal Bankruptcy Law (`11 U.S.C. §§ 362(a), 524(a)` and *Taggart v. Lorenzen*):**
   - The underlying lawsuit is a Duval County, Florida residential landlord-tenant dispute (`Case No. 16-2024-CC-000687`) in which tenants Nathaniel Chibuzor Keita and Lana Paige Tompkins obtained an August 2024 bench-trial judgment (`$7,632.31` principal plus `$17,341.20` attorneys' fees and costs, totaling `$24,973.51`) against their landlords (petitioners) after constructive eviction from a townhome, followed by a November 2024 writ of garnishment against petitioners' bank accounts.
   - In March 2025—while petitioners' appeal was pending in the Florida Fifth District Court of Appeal (`5D2024-2417`)—one of the two judgment creditors, Respondent Keita, filed a voluntary Chapter 7 bankruptcy petition in the Middle District of Florida (`3:25-bk-00977-BAJ`), receiving a no-asset discharge on July 2, 2025.
   - Petitioners' primary federal theory under Question Presented 1 is that Keita's Chapter 7 bankruptcy triggered the `11 U.S.C. § 362(a)` automatic stay to render the Fifth DCA's May 1, 2025 *pro se* barring order and August 12, 2025 *per curiam* affirmance void *ab initio*, and that Keita's `11 U.S.C. § 524(a)` discharge injunction (and *Taggart v. Lorenzen*, 587 U.S. 554 (2019)) extinguished petitioners' debt and bars garnishment.
   - That theory inverts the Bankruptcy Code:
     - Under `11 U.S.C. § 362(a)(1)–(2)`, the automatic stay halts actions and judgment enforcement **against the debtor** (`Keita`), not actions or judgments in which the bankruptcy debtor is the **plaintiff/judgment creditor** and a non-bankrupt third party (`Gnanam`) is the judgment debtor.
     - Under `11 U.S.C. § 524(a)`, a bankruptcy discharge voids judgments and enjoins collection with respect to the **personal liability of the debtor** (`Keita`). Keita's Chapter 7 discharge discharged *Keita's* debts to his creditors; it did not discharge *petitioners'* judgment liability to Keita (much less to co-plaintiff Lana Paige Tompkins, who never filed for bankruptcy). *Taggart v. Lorenzen* (`scotus/15006766`), which sets the objective "fair ground of doubt" standard for holding a creditor in civil contempt for collecting a discharged debt *from the bankruptcy debtor*, has no bearing on a third-party judgment debtor seeking to avoid paying a state-court judgment.
     - As for `11 U.S.C. §§ 541(a)(1)` and `554(d)` (Keita's failure to schedule his interest in the state-court judgment on Schedule A/B), any unscheduled asset belongs to the Chapter 7 bankruptcy estate for the benefit of Keita's creditors (administered by reopening the bankruptcy case under `11 U.S.C. § 350(b)` so the Chapter 7 trustee can collect the judgment from petitioners)—it does not void the state judgment or absolve the judgment debtors of liability.

3. **Severe Jurisdictional, Preservation, and Vehicle Defects under `28 U.S.C. § 1257(a)`:**
   - **Decision Below & Preservation:** The Fifth DCA entered an unelaborated `PER CURIAM. AFFIRMED.` on August 12, 2025 (`Appendix B`), and the Florida Supreme Court dismissed discretionary review for lack of jurisdiction over an unelaborated PCA on August 18, 2025 (`Appendix A`). The federal bankruptcy arguments were not raised before or decided by the Fifth DCA in `5D2024-2417`; rather, petitioners raised them for the first time in post-mandate motions in the Duval County Court beginning in September 2025 (`Appendices P, Q, T`).
   - **Split Proceedings & Post-Mandate Trial Court Orders:** Although Justice Thomas granted an extension of time to January 15, 2026 in `25A442` to petition from the August 2025 appellate orders, petitioners repeatedly revised their petition during Rule 14.5 cure rounds through November 2026 to challenge post-mandate Duval County Court orders entered in December 2025, March 2026 (`Appendix P`), and July 2026 (`Appendix Q-4`) by County Judges Shayla E. Lee and Kristen Brooke Stephens Brady—trial-court orders that have not been reviewed by a state appellate court as required by `28 U.S.C. § 1257(a)`.
   - **Fact-Bound State Procedural Issues (QP 2):** Petitioners' remaining arguments—whether County Judges Lee and Brady were automatically disqualified under `Fla. R. Gen. Prac. & Jud. Admin. 2.330(l)` for exceeding the 30-day ruling window, whether the March 4, 2026 *nunc pro tunc* written orders (`Appendix P`) were ministerial memorials of the October 17, 2025 oral rulings (`Appendix T-1`), and whether respondents' counsel timely answered petitioners' garnishment exemption claim under `Fla. Stat. § 77.041(3)`—are pure questions of Florida procedure that do not present a substantial federal question under *Caperton v. A.T. Massey Coal Co.*, 556 U.S. 868 (2009).

## 4. Secondary Claims and Distribution Calibration

- **`disposition` (`0.002`):** Matches top-level `probability = 0.002`.
- **`relist-increment` (`0.96`):** At `moment: arrival`, `context.distribution_count` is `0`. Because `relist-increment` resolves `outcome.distribution_count > context.distribution_count`, any petition that survives to its initial conference distribution (`distribution_count >= 1`) resolves this increment true. In the paid scored segment, ~96% of newly docketed petitions are distributed at least once (with ~3–4% dismissed beforehand under Rule 46 or Rule 14.5). By contrast, the probability that the petition is relisted *after* its first conference (`distribution_count >= 2`) is only ~1.5%.
- **`cvsg-increment` (`0.001`):** Near-zero probability of an SG invitation in a *pro se* landlord-tenant dispute.
- **`summary-disposition-route` (`0.35`):** Conditional on a grant, a summary GVR to address the post-judgment bankruptcy estate standing question is weighted at `35%` (comparable to the ~31% historical GVR share of grants in the paid scored segment: `76` GVRs vs. `169` full grants in the `relist` / `CVSG` paid-segment tables).
- **`dissent-from-denial` (`0.002`) & `order-writers` (`0.0001`–`0.0005`):** Given the *pro se* posture, inverted bankruptcy theory, and `28 U.S.C. § 1257(a)` finality/preservation barriers, there is virtually no prospect of a separate writing respecting denial.
- **`big_case_score` (`0.02`):** A localized `$24,973.51` county-court landlord-tenant judgment with no national policy, institutional, or doctrinal stakes.
