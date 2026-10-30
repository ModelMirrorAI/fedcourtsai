# Prediction Reasoning: *Richard Stuart Ross v. United States* (No. 26-91)

- **Case ID**: `scotus/9026000091`
- **Event ID**: `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`)
- **Input Snapshot**: `2026-09-09.json` (cutoff `2026-09-10`, `mode: forward`, `band: baseline`, `salience_version: sal-v4`, `distribution_count: 1`, `term: 2026`)
- **Prediction**: **Denied** (`granted: 0`, `probability: 0.10`, `predicted_disposition: "denied"`)

---

## 1. Case Overview and Provisioned Inputs

This forecast is formed from the provisioned snapshot (`record/snapshots/2026-09-09.json`), `record/context.json`, and the three provisioned document files in `record/documents/` (`questions-presented.txt`, `petition.txt`, and `appendix.txt`, all complete and non-OCR). Because the cell is placed at the `response-requested` moment (opened September 9, 2026, when the Court called for a response after the Solicitor General's August 10, 2026 waiver), no Brief in Opposition or reply brief exists in the baseline record.

In October 2021, $29,583,354.63 belonging to a defense contractor ("Company 1" / "Phoenix") was diverted in a business-email-compromise wire fraud into a Regions Bank IOTA client trust account held by Petitioner Richard Stuart Ross, a Florida attorney. Before October 7, 2021, the account held $3,877.33. During October 2021, two wires totaling $1,213,113.11 (primarily proceeds from the sale of Ross's personal home, which Ross commingled into his client trust account) were also deposited into the account, while over $25 million was rapidly wired out to accounts in Mexico and elsewhere in transactions Ross helped direct (App. 8a–10a, 42a–44a).

In November 2021, the federal government seized $4,905,730.26 from the Regions accounts and filed a verified civil forfeiture complaint in the Northern District of New York in February 2022 under 18 U.S.C. §§ 981 and 984. Both Ross and Phoenix filed claims solely to $1,213,113.11 (the "Contested Funds"); no claims were filed as to the remaining $3,692,617.15 (the "Uncontested Funds").

In November 2022—nine months after filing the complaint and prior to discovery—the government moved under Federal Rule of Civil Procedure 41(a)(2) to voluntarily dismiss the forfeiture action *without prejudice* as to the $1,213,113.11 Contested Funds while obtaining a default forfeiture judgment as to the $3,692,617.15 Uncontested Funds. On March 2, 2023, Senior District Judge Gary L. Sharpe granted the partial default judgment forfeiting the $3.69 million, granted voluntary dismissal *without prejudice* as to the $1.21 million over Ross's objection, and issued a certificate of reasonable cause under 28 U.S.C. § 2465(a)(2) (App. 61a–68a). After waiting 60 days to confirm that competing claimant Phoenix would not appeal, the government returned the $1,213,113.11 to Ross in May 2023.

On March 22, 2024, Senior District Judge Frederick J. Scullin, Jr. denied Ross's motion for attorney's fees, costs, and interest under the Civil Asset Forfeiture Reform Act of 2000 ("CAFRA"), 28 U.S.C. § 2465(b)(1)(A), on two independent grounds (App. 53a–60a):
1. Ross did not "substantially prevail" because a voluntary dismissal without prejudice lacks the judicially sanctioned material alteration of the parties' legal relationship required under *Buckhannon Board & Care Home, Inc. v. West Virginia Dept. of Health & Human Resources*, 532 U.S. 598 (2001); and
2. Independently, CAFRA's "multiple claims exception," 28 U.S.C. § 2465(b)(2)(C), barred a fee award because both Ross and Phoenix claimed portions of the seized property, the government promptly recognized and returned the $1.21 million once divisible, caused no superfluous litigation expense, and prevailed in forfeiting the remaining $3.69 million.

On December 5, 2025, the Second Circuit (Raggi, J., joined by Lohier and Carney, JJ.) vacated the certificate of reasonable cause (on the government's concession that § 2465(a)(2) applies only upon entry of a "judgment for the claimant") but affirmed the Rule 41(a)(2) dismissal without prejudice and the denial of CAFRA fees and interest. *United States v. Ross*, 161 F.4th 108 (2d Cir. 2025) (App. 1a–52a). Rehearing en banc was denied on February 17, 2026 (App. 69a–70a).

Ross filed a paid petition for certiorari on July 17, 2026 (docketed July 21, 2026). After the Solicitor General waived a response on August 10, 2026, eight cert-stage amicus briefs were filed between August 19 and August 21, 2026 (by the Goldwater Institute, NACDL, Separation of Powers Clinic, Americans for Prosperity Foundation, Advancing American Freedom et al., Atlantic Legal Foundation, Manhattan Institute, and Institute for Justice). The petition was distributed on August 26, 2026 for the September 28, 2026 conference, and on September 9, 2026, the Court called for a response (due October 9, 2026).

---

## 2. Base-Rate Anchoring (`metrics/statpack.md`)

1. **Salience Band Anchor (`baseline` under `sal-v4`)**:
   - `record/context.json` freezes `band: "baseline"`, `salience_version: "sal-v4"`, `distribution_count: 1`, `term: 2026`.
   - In `metrics/statpack.md` (*"Segment base rate by salience band (sal-v4)"*), pooling the bracketed `reached` rate for `baseline` across all nine rendered Terms strictly preceding OT2026 (OT2017–OT2025: `4.0% (n=1314)` in 2025, `5.9% (n=1274)` in 2024, `5.9% (n=1312)` in 2023, `5.9% (n=1196)` in 2022, `5.7% (n=1500)` in 2021, `4.5% (n=1740)` in 2020, `4.7% (n=1399)` in 2019, `4.8% (n=1529)` in 2018, and `4.9% (n=1649)` in 2017) yields a weighted pool of **n = 12,913** resolved petitions and ~659 grants, or a pooled `baseline` `[reached]` grant rate of **5.1%**.
2. **Overall and Signal Cuts (`metrics/statpack.md`)**:
   - **Modern discretionary-cert petitions by disposition**: Across 44,777 weighted resolved petitions, `denied` is 95.1% (42,577), `dismissed` is 2.1% (918), `granted` is 1.5% (692), and `gvr` is 1.3% (590) — a combined grant-family rate of **2.9%**.
   - **Originating circuit (`ca2`)**: Across `n=2,070` weighted resolved petitions from the Second Circuit, `denied` is 92.5%, `granted` is 2.7%, `dismissed` is 2.5%, and `gvr` is 2.4% (grant family **5.1%**).
   - **Relist count (paid scored segment)**: `relist_bucket = 0` (`n=10,203` resolved) has a grant-family rate of 1.8% (`granted` 1.3%, `gvr` 0.5%); `relist_bucket = 1` (`n=2,538` resolved) has a grant-family rate of 13.7% (`granted` 8.5%, `gvr` 5.2%); `relist_bucket = 2` (`n=495` resolved) is 41.2%; and `3+` (`n=484` resolved) is 37.4%. Note that because our snapshot stops on the day of the Call for a Response (`2026-09-09`), before the September 28 conference, the petition is guaranteed to be redistributed (`relist_bucket >= 1`) once the response arrives.
   - **CVSG status (paid scored segment)**: `none` (`n=13,556` resolved) has a grant-family rate of 6.4% (`granted` 4.1%, `gvr` 2.3%).
   - **Amicus-brief count (paid scored segment)**: Petitions with `2+` cert-stage amicus briefs (`n=1,449` resolved) have a terminal grant-family rate of **22.9%** (`granted` 18.4%, `gvr` 4.5%, `denied` 76.0%), compared to 15.1% for `1` brief (`n=1,162`) and 3.8% for `0` briefs (`n=11,109`).

---

## 3. Case-Specific Adjustments from the Anchor

Starting from the **5.1%** `baseline` `[reached]` anchor, the Call for a Response after the government's waiver and the mobilization of **eight cert-stage amicus briefs** from prominent repeat-player organizations (Institute for Justice, NACDL, Goldwater Institute, AFPF, Manhattan Institute, Atlantic Legal Foundation, Separation of Powers Clinic, Advancing American Freedom) justify a substantial upward adjustment (toward ~18%–22% based on the `2+` amicus cut and CFR posture). However, three severe legal and vehicle obstacles revealed in `petition.txt` and `appendix.txt` push the grant probability back down to **0.10 (10%)**:

### A. Complete Absence of a Circuit Split on Question 1 and Weak Split Claim on Question 2

Petitioner explicitly concedes (Pet. 3, 12–15) that there is **no circuit split** on Question 1. Every circuit to address whether the government's voluntary dismissal without prejudice makes a claimant a "substantially prevailing" party under CAFRA, 28 U.S.C. § 2465(b)(1)(A), has held that it does not:
- **Second Circuit**: *United States v. Ross*, 161 F.4th 108, 119–22 (2d Cir. 2025).
- **Fifth Circuit**: *United States v. $70,670.00 in U.S. Currency*, 929 F.3d 139, 143–46 (5th Cir. 2019).
- **Eighth Circuit**: *United States v. $32,820.56 in U.S. Currency*, 838 F.3d 930, 934–37 (8th Cir. 2016).
- **Ninth Circuit**: *United States v. $60,000 in U.S. Currency*, 763 F. App'x 640, 641 (9th Cir. 2019); *United States v. Ito*, 472 F. App'x 841, 842 (9th Cir. 2012).

On Question 2 (whether losing the opportunity to seek CAFRA fees constitutes "plain legal prejudice" barring a Rule 41(a)(2) dismissal without prejudice), the Second, Fifth, and Eighth Circuits are likewise aligned that the loss of potential CAFRA fee eligibility cannot itself be plain legal prejudice—otherwise *every* Rule 41(a)(2) dismissal in a CAFRA case would have to be with prejudice, nullifying Rule 41(a)(2)'s textual default (App. 40a–41a; 929 F.3d at 143; 838 F.3d at 936). Petitioner's alleged split relies on an unpublished, three-paragraph Ninth Circuit memorandum disposition (*Ito*, 472 F. App'x at 842) involving a self-contradictory district court order—which the Ninth Circuit itself later declined to follow in *$60,000 in U.S. Currency*, 763 F. App'x at 641—and general Tenth Circuit multi-factor Rule 41(a)(2) decisions (*Brown v. Baeke*, 413 F.3d 1121, 1124 (10th Cir. 2005)) that apply the same discretionary factors as the Second Circuit's *Zagano* test.

### B. Doctrinal Headwinds Under *Buckhannon* and *Lackey v. Stinnie* (2025)

Just last Term, in *Lackey v. Stinnie*, 604 U.S. 192 (2025), a 7–2 majority reaffirmed *Buckhannon*'s rule that statutory fee-shifting provisions keyed to "prevailing" require an **enduring, judicially sanctioned** change in the parties' legal relationship, rejecting fee recovery where government action moots a claim without final judicial relief. Even the *Lackey* dissenters (Justice Jackson, joined by Justice Sotomayor) agreed that *Buckhannon* requires a *judicially sanctioned* change. Moreover:
1. In an *in rem* forfeiture action, Congress used "the claimant substantially prevails" rather than "prevailing party" because the property owner is a "claimant" (not a formal "party") who may prevail as to a substantial portion of the seized res—not to adopt the catalyst theory.
2. When Congress wanted "substantially prevailed" in FOIA to cover a "voluntary or unilateral change in position by the agency," it amended FOIA in 2007 to add that explicit definition *"[f]or purposes of this subparagraph"* only (5 U.S.C. § 552(a)(4)(E)(ii)), while leaving CAFRA untouched (App. 30a–31a n.13).
3. CAFRA's fee-shifting provision is a waiver of federal sovereign immunity that must be strictly construed (*Ruckelshaus v. Sierra Club*, 463 U.S. 680, 685 (1983)).

### C. Severe Vehicle Defects: The Multiple-Claims Exception (`28 U.S.C. § 2465(b)(2)(C)`) and Underlying Fraud Facts

Even if four Justices were interested in revisiting how *Buckhannon* and *CRST Van Expedited, Inc. v. EEOC*, 578 U.S. 419, 433–34 (2016), apply to non-preclusive dismissals in civil forfeiture actions, the Solicitor General's Brief in Opposition will highlight two major vehicle problems:
1. **Alternative Statutory Holding Below**: Judge Scullin expressly held in the alternative that even if Ross had "substantially prevailed," he was barred from recovering fees under CAFRA's multiple-claims exception, 28 U.S.C. § 2465(b)(2)(C), because both Ross and fraud victim Phoenix filed competing claims to the $1.21 million, the government forfeited the remaining $3.69 million in the account, and the government promptly returned the $1.21 million once Phoenix's appeal window expired (App. 58a–60a). Because § 2465(b)(2)(C) provides an independent statutory ground supporting the judgment below, reversing on Question 1 or Question 2 would likely not entitle Ross to fees.
2. **Unattractive Factual Record and Concession of No Bad Faith**: The seized account was an attorney IOTA trust account into which $29.58 million stolen from a defense contractor was funneled and wired to Mexico in transactions Ross helped direct, and into which Ross commingled $1.20 million of personal home-sale proceeds (App. 8a–10a, 42a–44a). Further, Ross's counsel expressly disclaimed any contention of government bad faith at oral argument (App. 47a n.20), and the government moved to dismiss only nine months after filing the complaint, before discovery.

---

## 4. Secondary Claims and Uncertainties

- **`relist-increment` (0.99)**: Because the Court called for a response on September 9, 2026 (due October 9, 2026) while the petition was distributed once for the September 28 conference, the petition is virtually certain to be distributed at least once more after the Brief in Opposition arrives.
- **`cvsg-increment` (0.00)**: The United States is the Respondent represented by the Solicitor General, so a CVSG will not occur.
- **`summary-disposition-route` (0.05)**: Conditional on a grant, plenary review (~95%) is far likelier than a summary disposition (~5%) because there is no intervening decision supporting vacatur and four circuits have ruled for the government.
- **`dissent-from-denial` (0.12) & `order-writers`**: Given the eight amicus briefs and the CFR, there is a ~12% chance that a Justice (most likely Justice Thomas at `0.07` or Justice Gorsuch at `0.06`) authors a dissent from or statement respecting the denial of certiorari addressing civil forfeiture practices.
- **Note on Retrieval**: During this run, two attempted CourtListener MCP searches (`648 F.3d 946` and `Brown v. Baeke`) returned HTTP 429 daily rate-limit errors; we relied on the provisioned record (`petition.txt` and `appendix.txt`) and `fedcourts query` / `metrics/statpack.md`, which fully sufficed.
