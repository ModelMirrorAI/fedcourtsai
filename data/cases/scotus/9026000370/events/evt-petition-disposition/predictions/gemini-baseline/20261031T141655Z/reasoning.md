# Certiorari Disposition Rationale — *The Nielsen Company (US), LLC v. Cumulus Media New Holdings Inc.* (No. 26-370)

## Summary of Numbers

- **`granted`:** `0` (`predicted_disposition: "denied"`)
- **`probability` (`disposition`):** `0.04` (4.0%)
- **`relist-increment`:** `0.25` (25.0%)
- **`cvsg-increment`:** `0.03` (3.0%)
- **`summary-disposition-route`:** `0.10` (10.0% conditional on grant)
- **`dissent-from-denial`:** `0.025` (2.5% conditional on denial)
- **`big_case_score`:** `0.65`

---

## 1. Base-Rate Anchor and Docket Position

From `record/context.json`, this cell is a forward certiorari prediction (`mode: "forward"`, `term: 2026`, `band: "baseline"`, `salience_version: "sal-v6"`). The pre-computed 10-Term pooled risk-set anchor in `context.json` (`cert_anchor.rate`) is **0.05188** (~5.2%), which pools the `baseline` reached risk-set rate across the ten most recent Terms in `metrics/statpack.md` (OT2017–OT2026).

In `metrics/statpack.md`:
- **"Segment base rate by salience band (sal-v4)"**: Across OT2017–OT2025, private-party paid petitions that start in `baseline` have a `reached` grant rate of **4.0% to 5.9%** (e.g., OT2025: `1.0% (n=994) [reached 4.0%, n=1314]`; OT2024: `1.4% (n=936) [reached 5.9%, n=1274]`). Petitions that *terminate* in `baseline` (never receiving a response call, relist, or CVSG) grant at only **0.6% to 1.9%**.
- **"Cert petitions by relist count (paid scored segment)"**: Petitions resolving at `0` relists (`n=10204`) have a base rate of `denied 96.8%, dismissed 1.3%, granted 1.3%, gvr 0.5%` (1.8% grant family), whereas `1` relist (`n=2532`) sits at `granted 8.3%, gvr 5.2%` (13.5% grant family), and `2` relists (`n=495`) sits at `granted 28.3%, gvr 12.9%` (41.2% grant family).
- **"Cert petitions by CVSG status (paid scored segment)"**: Petitions without a CVSG (`none`, `n=13549`) grant at `4.1%` (`gvr 2.3%`), whereas petitions with a CVSG (`cvsg`, `n=164`) grant at `29.3%` (`gvr 5.5%`).
- **"Cert petitions by amicus-brief count (paid scored segment)"**: Petitions with `0` cert amici (`n=11109`) have a grant rate of `2.0%` (`gvr 1.8%`); `1` cert amicus (`n=1158`) sits at `10.1%` (`gvr 4.7%`); and `2+` cert amici (`n=1446`) sits at `18.2%` (`gvr 4.5%`, total grant family 22.7%).

On the provisioned snapshot (`2026-10-31.json`), the petition was filed September 15, 2026 (docketed September 17, 2026). On October 19, 2026, Respondent Cumulus Media New Holdings Inc. filed a **waiver of right to respond**, while two cert-stage amicus briefs were filed (by Washington Legal Foundation and by Law and Economics Scholars). On October 28, 2026, the petition was distributed for the Conference of November 13, 2026 (`distribution_count: 1`). There has been no response requested (`response_requested: null`) and no CVSG.

Because the Court does not grant plenary review off a waiver without first calling for a response (CFR) and redistributing the case once the brief in opposition arrives, any path to a grant requires first clearing the CFR hurdle (~25% probability here).

---

## 2. Case-Specific Adjustments from the 5.2% Anchor

### Upward Factors (Supporting a CFR and Potential Review)

1. **Experienced Supreme Court Counsel and Two Cert-Stage Amici:**
   - Petitioner Nielsen is represented by Thomas H. Dupree Jr. and Helgi C. Walker of Gibson, Dunn & Crutcher LLP.
   - Two respected institutional/academic amici (Washington Legal Foundation and Law and Economics Scholars affiliated with the International Center for Law & Economics) filed timely amicus briefs supporting Petitioner on October 19, 2026. In the paid scored segment, `2+` cert amici (`n=1446`) is a strong stakes signal, though when paired with a respondent waiver its immediate effect is primarily to raise the probability of a CFR (`relist-increment: 0.25`).
2. **Doctrinal Salience of the Sherman Act Section 2 Pricing / Tying Question:**
   - The petition forcefully argues that the Second Circuit's published opinion (*Cumulus Media New Holdings Inc. v. The Nielsen Co. (US), LLC*, 182 F.4th 108 (2d Cir. July 13, 2026)) deepens a twenty-year split over bundled discounts and price-based coercion under Section 2 of the Sherman Act—pitting the Third Circuit (*LePage's Inc. v. 3M*, 324 F.3d 141 (3d Cir. 2003) (en banc)) and now the Second Circuit against the Ninth and Sixth Circuits (*Cascade Health Solutions v. PeaceHealth*, 515 F.3d 883 (9th Cir. 2008); *Collins Inkjet Corp. v. Eastman Kodak Co.*, 781 F.3d 264 (6th Cir. 2015)), which require showing that a bundled discount or price differential is the economic equivalent of below-cost predation under *Brooke Group Ltd. v. Brown & Williamson Tobacco Corp.*, 509 U.S. 209 (1993), and *Pacific Bell Telephone Co. v. linkLine Communications, Inc.*, 555 U.S. 438 (2009).

### Downward Factors (Severe Vehicle Defects Weighing Against Certiorari)

1. **Interlocutory Preliminary-Injunction Posture and Undeveloped Cost Record:**
   - The Second Circuit's decision affirmed a preliminary injunction under an abuse-of-discretion / clear-error standard of review, explicitly stressing the preliminary posture throughout the opinion: *"On this preliminary posture, we resolve them in favor of Cumulus, mindful of the deference we owe to the district court's factual findings and discretionary decisions"* (Pet. App. 5a; see also Pet. App. 29a, 33a, 37a, 41a–42a).
   - Crucially, on the cost issue central to the Question Presented, the Second Circuit noted that *"Though Nielsen may later 'quantify [its] costs or correlate them with its price for standalone Nationwide,' id. at \*15, the record as it stands supports the conclusion that 'the difference in price cannot be legitimately justified by cost considerations'"* (Pet. App. 33a). That makes this appeal a poor vehicle for establishing a bright-line cost rule when the record on costs has not yet been developed on the merits.
2. **Unappealed Express-Tie Finding Below Blurs the Alleged Circuit Split:**
   - The district court held that Nielsen's 2024 "Network Policy" (which withheld local market data from the Nationwide report—"Swiss cheese" Nationwide—unless the broadcaster bought Nielsen's local data in every market where it owned stations) was an unlawful *express* tie, and **Nielsen did not challenge that holding on appeal** (Pet. App. 23a, 31a–32a).
   - The Second Circuit therefore analyzed Nielsen's lone standalone price quote—offered only after a cease-and-desist letter, at 10x Cumulus's existing contract allocation and 150% above the highest rate paid by any other network—not as an ordinary bundled-discount case, but as a de facto continuation and evasion of an uncontested express tie under *United States v. Loew's Inc.*, 371 U.S. 38 (1962), and *American Manufacturers Mutual Insurance Co. v. American Broadcasting-Paramount Theatres, Inc.*, 388 F.2d 272 (2d Cir. 1967) (Pet. App. 26a–30a).
   - If the Court calls for a response, Cumulus's brief in opposition will emphasize that *Cascade Health* and *Collins Inkjet* did not involve a defendant attempting to perpetuate an unappealed express tie via a single mid-negotiation price quote after months of refusing to sell the tying product separately.
3. **Active Parallel Proceedings in the Lower Courts (Chapter 11 Stay and Second Appeal):**
   - Two ongoing lower-court developments further undermine vehicle suitability:
     - First, Cumulus filed a voluntary Chapter 11 bankruptcy petition on March 10, 2026, and the district court stayed merits litigation of both Cumulus's claims and Nielsen's counterclaims (Pet. App. 14a–15a).
     - Second, as disclosed in the petition (Pet. 10–11) and confirmed on the Second Circuit's docket (No. 26-2516), subsequent district-court enforcement proceedings over new standalone offers by Nielsen (at less than half the price condemned in the first appeal) resulted in a September 9, 2026 order that is currently stayed and under active expedited review in a second Second Circuit appeal calendared for argument in November 2026.
   - The Court strongly disfavors granting interlocutory review when ongoing enforcement appeals and bankruptcy proceedings in the lower courts may moot, alter, or overtake the preliminary injunction under review.

---

## 3. Calibration of Final Probabilities

- **`probability` / `disposition` = `0.04`:** Starting from the `0.0519` 10-Term `baseline` risk-set anchor, the combination of Respondent's waiver and the pronounced interlocutory/vehicle defects outweighs the upward pressure from Gibson Dunn's advocacy and the two amicus briefs. There is roughly a 25% chance of a CFR (`relist-increment: 0.25`), and conditional on a CFR and brief in opposition, roughly a 16% chance of a grant once the vehicle flaws are fully aired ($0.25 	imes 0.16 = 0.04$).
- **`relist-increment` = `0.25`:** Reflects the probability that at least one Justice calls for a response (which requires redistributing the petition after the BIO is filed) or relists the petition from the November 13, 2026 Conference.
- **`cvsg-increment` = `0.03`:** Very low given the interlocutory posture and active second appeal, even though the Court called for the SG's views in *LePage's* in 2004.
- **`summary-disposition-route` = `0.10`:** Conditional on a grant, the Court would almost certainly set the case for plenary briefing and argument rather than issuing a summary reversal or GVR.
- **`dissent-from-denial` = `0.025` and `order-writers`:** Small probability (~2.5%) that a Justice (most plausibly Gorsuch, Thomas, or Alito) writes a brief statement or dissent respecting the denial of certiorari to flag the *linkLine* / constructive-tying issue for a future final-judgment vehicle.
- **`big_case_score` = `0.65`:** If decided on the merits, a Supreme Court ruling on whether above-cost standalone-versus-bundle price differentials can constitute unlawful coercion or "constructive tying" under Section 2 of the Sherman Act would be a major antitrust precedent for multiproduct firms across the economy (already cited in the *Live Nation* and *Google Ad Tech* monopolization cases), even though its grant likelihood in this interlocutory posture is low.
