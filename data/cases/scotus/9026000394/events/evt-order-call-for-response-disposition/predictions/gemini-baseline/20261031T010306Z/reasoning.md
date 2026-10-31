# Prediction Reasoning: *Michael Herlihy, et al. v. DBMP, LLC* (No. 26-394)

**Event:** `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`)  
**Predicted Disposition:** `denied` (`granted: false`, `probability: 0.14`)  
**Big-Case Score:** `0.72`

---

## 1. Base Rate & Trajectory Anchor

From `record/context.json` and `metrics/statpack.md` (under `sal-v4`, restricted to complete and resolved prior Terms OT2017–OT2025 before the OT2026 anchor):
- The petition is a paid certiorari petition from the Fourth Circuit (`ca4`) by private petitioners (`Michael Herlihy, et al.`), placing it in the **`baseline` band** at the `response-requested` moment (`relists: 0`, `cvsg: false`).
- The pre-pooled `cert_anchor` (`sal-v4` `baseline` risk-set rate across prior Terms) is **5.09%** (`0.05089`, 597 grants out of 11,731 weighted-resolved petitions).
- However, this event is conditioned on `moment: response-requested`. On September 29, 2026, Respondent DBMP, LLC waived its right to respond; the petition was distributed on October 14, 2026 for the October 30, 2026 conference; and on October 20, 2026 (prior to the conference sitting), the Court requested a response, due November 19, 2026. Historically, a Call for Response (CFR) after a waiver removes a petition from the summary-denial pool of unrequested waivers and shifts the conditional grant rate into the ~8%–12% range before accounting for case-specific factors and subsequent relists.

---

## 2. Case Overview & Procedural Posture

This case arises out of the long-running "Texas Two-Step" asbestos bankruptcy of DBMP, LLC—a divisional-merger spin-off created in October 2019 by CertainTeed Corporation (a solvent subsidiary of Saint-Gobain). Under the divisional merger:
- Old CertainTeed split into (1) New CertainTeed, which received roughly 97% of the operating assets, and (2) DBMP, which received all of Old CertainTeed's hundreds of thousands of asbestos tort liabilities (~$1.5 billion estimated) along with a Funding Agreement from New CertainTeed to backstop allowed asbestos claims in bankruptcy.
- Ninety-one days later (January 2020), DBMP filed for Chapter 11 in the Western District of North Carolina (Charlotte Division), seeking to channel all asbestos claims into a 11 U.S.C. § 524(g) trust.

**Crucial Procedural Feature:** Neither the Official Committee of Asbestos Claimants nor any claimant moved to dismiss DBMP's Chapter 11 petition for bad faith under 11 U.S.C. § 1112(b) at the outset of the bankruptcy, because Fourth Circuit precedent (*Carolin Corp. v. Miller*, 886 F.2d 693 (4th Cir. 1989)) requires a party seeking dismissal for lack of good faith to prove *both* (1) objective futility of reorganization and (2) subjective bad faith.

Instead, in 2022–2023—more than two years into the bankruptcy—Petitioners (Michael and Ann Herlihy and the Estate of Peter Bergrud, two individual mesothelioma claimants whose state-court suits were stayed on the eve of trial or judgment) moved to lift the automatic stay for "cause" under **11 U.S.C. § 362(d)(1)**. The bankruptcy court (Judge Whitley) denied stay relief (while criticizing *Carolin* as overly indulgent toward Texas Two-Step debtors), the district court affirmed, and a divided Fourth Circuit panel affirmed (2–1).
- **Majority (Judge Niemeyer, joined by Judge Rushing):** Held that (1) under *Carolin*, DBMP's Chapter 11 petition was not objectively futile because DBMP has ongoing real estate business, 60,000+ asbestos claims, and a Funding Agreement capable of funding a § 524(g) trust; (2) Petitioners waived any standalone argument that subjective bad faith alone suffices under § 362(d)(1) by failing to raise it before the bankruptcy court; and (3) the bankruptcy court did not abuse its discretion under the *Robbins* balancing factors (`In re Robbins`, 964 F.2d 342 (4th Cir. 1992)) in declining to lift the stay for two claimants when thousands of other asbestos claimants remain stayed.
- **Dissent (Judge King):** Issued a forceful 45-page dissent arguing that *Carolin* itself recognized that when subjective bad faith is "extreme," a fuller inquiry into objective futility is unnecessary, and condemning the Texas Two-Step as an abusive manipulation of the Bankruptcy Code and seventh amendment jury-trial rights.
- **Rehearing En Banc:** Denied on April 20, 2026; remarkably, the order notes that **"No judge requested a poll under Fed. R. App. P. 40."**

---

## 3. Factors Favoring Certiorari

1. **A Acknowledged, High-Profile Circuit Split on Good Faith & Financial Distress:**
   - The Third Circuit in *In re LTL Management, LLC*, 64 F.4th 84 (3d Cir. 2023), held that a Chapter 11 debtor must be in immediate "financial distress" to file in good faith, dismissing Johnson & Johnson's Texas Two-Step bankruptcy because a parent funding agreement insulated the spin-off from financial distress.
   - Most other circuits employ a "totality of the circumstances" test for good faith under §§ 1112(b) and 362(d)(1), whereas the Fourth Circuit uniquely adheres to *Carolin*'s conjunctive two-prong test (requiring *both* objective futility and subjective bad faith), making the W.D.N.C. a magnet venue for Texas Two-Step filings (*Bestwall*, *DBMP*, *Aldrich Pump*, *Murray Boiler*).
   - Even the bankruptcy judge below noted that *Carolin*'s standard diverges from sister circuits and facilitates corporate engineering.
2. **Court-Ordered Call for Response + Vigorous Dissent Below:**
   - At least one Justice flagged the petition for a response before the October 30 conference despite DBMP's initial waiver.
   - Judge King's lengthy and pointed dissent highlights the national controversy over the Texas Two-Step, particularly in the wake of *Harrington v. Purdue Pharma L.P.*, 603 U.S. 204 (2024), and *Truck Insurance Exchange v. Kaiser Gypsum Co.*, 602 U.S. 268 (2024).

---

## 4. Factors Weighing Heavily Against Certiorari (Vehicle Flaws)

1. **Severe Vehicle Problems — § 362(d)(1) Stay Relief vs. § 1112(b) Dismissal:**
   - In *LTL Management*, creditors moved immediately at the outset of the case to **dismiss** the Chapter 11 petition under § 1112(b). Here, DBMP's Chapter 11 case was never sought to be dismissed for bad faith and has been pending in bankruptcy court since **January 2020** (over six years).
   - Petitioners are two individual tort claimants asking to lift the automatic stay under § 362(d)(1) to liquidate their claims in state court while leaving the underlying Chapter 11 case—and the automatic stay as to 60,000+ other claimants—intact.
   - As Respondent (represented by Noel Francisco at Jones Day) will inevitably emphasize in the Brief in Opposition, the Fourth Circuit held that **even setting *Carolin* aside**, the bankruptcy court permissibly denied stay relief under the traditional *Robbins* equitable balancing factors because lifting the stay for two claimants would prejudice the estate and trigger a flood of similar stay-relief motions by thousands of similarly situated claimants while the Chapter 11 case proceeds. That independent, fact-bound abuse-of-discretion holding under *Robbins* insulates the judgment below from a pure legal ruling on *Carolin*.
2. **Waiver Found by the Fourth Circuit:**
   - The Fourth Circuit majority explicitly held (App. 20a–21a) that Petitioners **waived** the argument that "subjective bad faith alone can constitute cause to lift the Automatic Stay" because they argued only *Carolin*'s two-prong test in the bankruptcy court and disclaimed asking the court to depart from *Carolin*. The Supreme Court strongly disfavors granting certiorari when the court of appeals held a core component of the petitioner's theory forfeited or waived below.
3. **No En Banc Poll Requested in the Fourth Circuit:**
   - Despite Judge King's 45-page panel dissent, **not a single active judge on the Fourth Circuit requested an en banc poll** under Fed. R. App. P. 40 (App. 80a; Judge King took senior status or did not request a poll, or agreed the vehicle was unsuitable). The absence of an en banc poll in a 15-judge circuit suggests the full Fourth Circuit viewed this specific appeal—a § 362(d)(1) motion filed years into a bankruptcy—as an unsuitable vehicle to revisit *Carolin*.
4. **Prior Denials in Related Fourth Circuit Texas Two-Step Petitions:**
   - Corpus queries confirm the Supreme Court has repeatedly denied certiorari in closely related Fourth Circuit Texas Two-Step appeals from W.D.N.C., including *Official Committee of Asbestos Claimants of Bestwall LLC v. Bestwall LLC*, No. 25-1013 (cert. denied June 1, 2026, from 148 F.4th 233 (4th Cir. 2025), despite six amicus briefs including Senators and bankruptcy scholars) and Nos. 23-675 & 23-702 (cert. denied May 13, 2024).
5. **Counsel Asymmetry:**
   - Petitioners are represented by regional bankruptcy counsel without a seasoned Supreme Court practice on the petition caption, whereas Respondent is represented by former Solicitor General Noel Francisco (Jones Day), who successfully opposed certiorari in *Bestwall* (Nos. 23-675, 23-702, and 25-1013). Moreover, no cert-stage amicus briefs appear on the docket prior to the October 31 snapshot.

---

## 5. Synthesis & Probability Calibration

Starting from the `sal-v4` `baseline` risk-set anchor of **5.1%** and adjusting upward for the Call for Response (~10%–12% conditional baseline) and the genuine, important circuit split with the Third Circuit's *LTL Management* decision (upward pressure toward ~20%–25%), I then apply a substantial downward adjustment for the severe vehicle defects: (a) the § 362(d)(1) stay-relief posture six years into an un-dismissed bankruptcy, (b) the independent *Robbins* balancing ground supporting affirmance, (c) the Fourth Circuit's explicit finding of waiver below, and (d) the Court's June 2026 denial of certiorari in *Bestwall* (No. 25-1013).

Balancing these considerations yields a grant probability of **0.14** (`14%`), with `predicted_disposition: "denied"` (`granted: false`).

---

## 6. Big-Case Score (`0.72`)

Decoupled from grant likelihood, *significance if decided* is high (**0.72**). If the Supreme Court were to grant certiorari and decide whether the Bankruptcy Code's good-faith requirement under §§ 362(d)(1) and 1112(b) requires immediate financial distress or bars divisional-merger ("Texas Two-Step") filings by solvent corporate groups, the ruling would reshape mass-tort Chapter 11 practice nationwide, directly resolving the rift between the Third Circuit (*LTL Management*) and the Fourth Circuit (*Carolin* / *Bestwall* / *DBMP*) and governing billions of dollars in asbestos, talc, and environmental mass-tort liabilities following *Purdue Pharma*.
