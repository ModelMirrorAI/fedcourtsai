# Certiorari Prediction: *Michael Herlihy, et al. v. DBMP, LLC* (No. 26-394)

- **Case ID:** `scotus/9026000394`
- **Event ID:** `evt-petition-disposition` (`stage: cert`, `moment: distribution`)
- **Input Snapshot:** `2026-10-31.json`
- **Prediction:** `granted: 0` (`predicted_disposition: "denied"`, `probability: 0.14`)
- **Big Case Score:** `0.72`

---

## 1. Base-Rate Anchor and Docket Signals

### Pre-computed Salience Anchor vs. Current Docket Trajectory
In `record/context.json`, the case carries `band: "baseline"` (`salience_version: "sal-v6"`), `distribution_count: 1`, `cvsg_date: null`, and a 10-Term lookback `cert_anchor` grant-family rate of **5.19%** (`0.051875`). That figure is the scored baseline for this cell.

However, the provisioned docket snapshot (`record/snapshots/2026-10-31.json`) reflects two substantial escalation signals that occurred between October 13 and October 30, 2026:
1. **Call for a Response (CFR) after Waiver:** Respondent DBMP, LLC waived its right to respond on October 22, 2026, and the petition was distributed on October 28 for the November 13, 2026 Conference (`distribution_count: 1`). On **October 30, 2026**, the Court requested a response (due November 30, 2026). Calling for a response removes the petition from the dead-on-arrival waiver pool and moves its forward trajectory into the `elevated` cohort. Across the 10-Term table in `metrics/statpack.md`, paid petitions reaching the `elevated` band resolve in the grant family (`granted` + `gvr`) at roughly **13.4% to 20.3%** (and end in the `elevated` band with a ~7.8% to 13.1% grant rate, vs. 10.2% pooled in the overall salience table).
2. **Five Cert-Stage Amicus Briefs:** Five amicus briefs supporting petitioners were filed at the certiorari stage:
   - *A Group of Bankruptcy Law Professors* (David R. Kuney)
   - *Official Committee of Asbestos Personal Injury Claimants* (Kevin C. Maclay, Caplin & Drysdale)
   - *Professor D. Theodore Rave* (Bret R. Vallacher, Massey & Gail)
   - *North Carolina, et al.* (coalition of States led by the North Carolina DOJ)
   - *Public Justice* (Laura R. Gerber, Keller Rohrback)
   In `metrics/statpack.md`, paid cert petitions in the `2+` cert-stage amicus bucket (`n = 581`) have a marginal grant-family rate of **22.7%** (18.2% granted, 4.5% GVR, with `unknown` amicus count on `n = 1,073`), while Fourth Circuit (`ca4`) paid petitions overall (`n = 1,452`) have a low grant-family base rate of **2.6%** (1.3% granted, 1.3% GVR).

Starting from the **5.19%** `cert_anchor` and updating upward to reflect the October 30 CFR and five cert-stage amicus briefs places the initial structural prior in the **15%–20%** range before evaluating case-specific vehicle quality and issue history.

---

## 2. Case-Specific Merits, Circuit Split, and Prior Denials

### The Issue and the Circuit Split (from `questions-presented.txt`, `petition.txt`, and `appendix.txt`)
In 2019, CertainTeed Corporation—a profitable building-products subsidiary of Compagnie de Saint-Gobain facing ~60,000 pending asbestos suits and $80–$110 million in annual asbestos defense and indemnity costs—executed a divisional merger under Texas law ("Project Horizon," a "Texas Two-Step"). It allocated 97% of its operating assets to "New CertainTeed" and all of its asbestos liabilities (plus a smaller operating subsidiary and an uncapped funding agreement from New CertainTeed) to a newly created North Carolina LLC, Respondent DBMP, LLC. DBMP then filed for Chapter 11 bankruptcy in the Western District of North Carolina to establish an asbestos channeling trust under 11 U.S.C. § 524(g), triggering an automatic stay under 11 U.S.C. § 362(a) and a preliminary injunction shielding New CertainTeed.

In April 2024, four years into the bankruptcy, two individual mesothelioma claimants (Petitioners Michael and Ann Herlihy and the Estate of Peter Bergrud) moved under 11 U.S.C. § 362(d)(1) to lift the automatic stay for "cause" so they could liquidate their state-law tort claims in California and Washington. They argued that DBMP's Texas Two-Step filing lacked good faith because DBMP and CertainTeed are financially healthy and not in financial distress.

A divided Fourth Circuit panel affirmed the denial of stay relief (`167 F.4th 142`, App. 1a–61a). Writing for the majority, Judge Niemeyer (joined by Judge Harris) held:
1. The bankruptcy court did not abuse its discretion under *In re Robbins*, 964 F.2d 342 (4th Cir. 1992), in concluding that lifting the stay for individual claimants would invite a flood of thousands of similar motions, prejudice the estate, and destroy the pending § 524(g) reorganization (App. 11a–12a).
2. Under Fourth Circuit precedent (*Carolin Corp. v. Miller*, 886 F.2d 693 (4th Cir. 1989); *In re Premier Automotive Services, Inc.*, 492 F.3d 274 (4th Cir. 2007)), establishing lack of good faith as "cause" under § 1112(b) or § 362(d) requires the movant to show *both* subjective bad faith *and* objective futility. Because DBMP faced 60,000 asbestos suits and sought a § 524(g) trust—which does not require insolvency—its solvency was "irrelevant" to bad faith and its reorganization was not objectively futile (App. 12a–18a).

Judge King dissented at length (App. 19a–61a), arguing that the Fourth Circuit has become a "safe haven" for wealthy corporations using the Texas Two-Step to evade tort liability, that § 362(g)(2) places the burden of disproving bad faith on the debtor opposing stay relief, and that a solvent enterprise lacking financial distress acts in bad faith. The Fourth Circuit denied rehearing en banc with no judge requesting a poll (App. 80a).

### Why the Circuit Split and Amicus Support Push Toward Review
- **Doctrinal Tension with the Third Circuit:** In *In re LTL Management, LLC*, 64 F.4th 84 (3d Cir. 2023), the Third Circuit dismissed Johnson & Johnson's Texas Two-Step bankruptcy under 11 U.S.C. § 1112(b), holding that good faith requires immediate financial distress and that an uncapped funding agreement from a wealthy parent negates financial distress. The Fourth Circuit's *Carolin* two-prong standard (subjective bad faith + objective futility) and its holding that financial distress is "irrelevant" when invoking § 524(g) stand in sharp tension with *LTL Management* as well as First, Fifth, Eighth, and Eleventh Circuit decisions treating financial distress as central to Chapter 11 good faith (Pet. 11–18).
- **Forum Concentration:** Because debtors can manufacture venue in the Western District of North Carolina, the Fourth Circuit's permissive standard attracts national mass-tort filings (*Bestwall*, *DBMP*, *Aldrich Pump*, *Murray Boiler*), limiting further circuit percolation (Pet. 23–25).
- **Experienced Counsel:** Deepak Gupta (Gupta Wessler LLP) is counsel of record for Petitioners, backed by five coordinated amicus briefs.

### Why Severe Vehicle Defects and Recent Precedent Weigh Heavily Against a Grant
Despite the prominence of the "Texas Two-Step" debate, three major countervailing factors make a grant of certiorari unlikely once Respondent DBMP (represented by C. Kevin Marshall of Jones Day) files its Brief in Opposition:

1. **The Court Just Denied Certiorari in *Bestwall* (No. 25-1013) Five Months Ago:**
   Corpus retrieval confirms that on **June 1, 2026**, the Supreme Court denied certiorari in *Official Committee of Asbestos Claimants of Bestwall LLC v. Bestwall LLC*, No. 25-1013 (arising from *Bestwall*, 148 F.4th 233 / 157 F.4th 579 (4th Cir. 2025)), after the Court had previously denied two earlier *Bestwall* petitions in May 2024 (Nos. 23-675 and 23-702). Notably, *Bestwall* No. 25-1013 featured virtually the *identical* amicus coalition supporting the asbestos claimants (Public Justice, Group of Bankruptcy Law Professors, Prof. D. Theodore Rave, Senators Durbin/Whitehouse/Hawley represented by Deepak Gupta, and the Asbestos Creditors' Committees in DBMP and Aldrich). The Court's repeated refusal to review the Fourth Circuit's Texas Two-Step asbestos cases—most recently in June 2026—strongly indicates that there are not four Justices eager to intervene in the W.D.N.C. asbestos bankruptcies at an interlocutory stage.

2. **Awkward § 362(d) Individual Lift-Stay Posture (Rather than a § 1112(b) Motion to Dismiss):**
   Petitioners frame this case as a "clean vehicle" to resolve the split with *LTL Management* (Pet. 25–26), but the procedural posture is actually much worse than *LTL Management*:
   - *LTL Management* was a direct motion by the Official Committee to **dismiss** the Chapter 11 case outright under 11 U.S.C. § 1112(b) at the threshold of the bankruptcy.
   - Here, **no party ever moved to dismiss DBMP's Chapter 11 petition under § 1112(b)** (App. 7a, 9a). Instead, four years into the bankruptcy—while the Official Committee is actively litigating adversary proceedings challenging the divisional merger inside the bankruptcy court (App. 34a, 38a)—two individual claimants out of 60,000+ moved to lift the automatic stay under § 362(d) solely for their own two state-court lawsuits.
   - As Judge Niemeyer emphasized for the Fourth Circuit majority, *"we do not have before us any motion to dismiss the Chapter 11 petition so as to challenge whether Chapter 11's § 524(g) reorganization procedure has been appropriately invoked in this case. Nor do we have the question before us whether the pre-bankruptcy Texas Two-Step process is appropriate or legal."* (App. 9a).

3. **Independent Discretionary Ground Under *In re Robbins*:**
   A decision whether to lift an automatic stay for individual creditors under § 362(d) is reviewed for **abuse of discretion** and is governed by the traditional equitable balancing factors of *In re Robbins*, 964 F.2d 342 (4th Cir. 1992). Both the bankruptcy court and the Fourth Circuit held that, in an active Chapter 11 case that has never been dismissed under § 1112(b), lifting the stay for two asbestos claimants would inevitably trigger thousands of copycat lift-stay motions and effectively destroy the bankruptcy case through the back door (App. 11a–12a, 35a–38a). Because a court cannot use an individual § 362(d) lift-stay motion as a collateral substitute for an unfiled § 1112(b) motion to dismiss, Respondent's forthcoming BIO will have a compelling argument that the case is a poor, fact-bound vehicle that cannot cleanly reach the broader *LTL Management* dismissal question.

---

## 3. Calibration of Declared Claims, Distribution Claims, and Big-Case Score

- **`disposition` / `probability` (`0.14`):** Balancing the genuine issue salience (reflected in the Call for a Response, five amicus briefs, and Judge King's dissent) against the serious vehicle problems of a collateral § 362(d) lift-stay appeal and the Court's June 2026 denial in *Bestwall* (No. 25-1013), I estimate a **14% probability (`0.14`)** that certiorari is granted (`granted: 0`, `predicted_disposition: "denied"`).
- **`relist-increment` (`0.96`):** The snapshot records `distribution_count: 1` (distributed October 28, 2026 for the November 13 Conference) followed by `Response Requested` on October 30, 2026 (response due November 30, 2026). Because a petition on which the Court calls for a response after initial distribution is redistributed for a new conference once the Brief in Opposition is filed (or its time expires), the resolution-time distribution count will rise above 1 unless the petition is withdrawn or dismissed under Rule 46 before re-distribution (~4% chance).
- **`cvsg-increment` (`0.05`):** In the paid scored segment (`metrics/statpack.md`), CVSGs occur in only `82 / 1,654` (`5.0%`) of petitions, and the Court did not invite the Solicitor General's views in any of the three prior *Bestwall* petitions. I set `cvsg-increment` at **0.05**.
- **`summary-disposition-route` (`0.03`):** Conditional on a grant, summary disposition (GVR or summary reversal) is very unlikely (`0.03`). In `metrics/statpack.md`, GVRs account for roughly 24% of all grants overall (`37 / 153`), but here *Truck Insurance Exchange v. Kaiser Gypsum Co.*, 602 U.S. 268 (2024), and *Harrington v. Purdue Pharma L.P.*, 603 U.S. 204 (2024), were both decided in June 2024 and already addressed below (App. 15a–16a), and `record/same-question.json` is empty (`petitions: []`). Any grant here would almost certainly be for plenary review of the Third/Fourth Circuit split.
- **`dissent-from-denial` (`0.08`) and `order-writers`:** Conditional on denial, a noted dissent or statement is uncommon (and none was filed in *Bestwall* No. 25-1013), but Judge King's forceful 43-page dissent and the salience of mass-tort bankruptcy abuses after *Purdue Pharma* create a modest (`0.08`) chance that a Justice writes separately—most likely Gorsuch (`0.025`), Thomas (`0.020`), Sotomayor (`0.015`), or Jackson (`0.015`), with lower probabilities for Alito (`0.010`), Kavanaugh (`0.008`), Kagan (`0.004`), Barrett (`0.004`), and Roberts (`0.002`).
- **`big_case_score` (`0.72`):** Decoupled from grant odds, a Supreme Court merits decision determining whether solvent corporations can use the Texas Two-Step divisional merger and Chapter 11 § 524(g) trusts without showing financial distress would be a major commercial and mass-tort bankruptcy precedent governing tens of thousands of asbestos claims and billions of dollars in tort liabilities (`0.72`).
