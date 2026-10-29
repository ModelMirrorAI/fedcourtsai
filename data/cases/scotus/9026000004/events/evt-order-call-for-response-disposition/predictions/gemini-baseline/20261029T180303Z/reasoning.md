# Reasoning: *Samsung Electronics America, Inc. v. Jordan Brewer* (No. 26-4)

**Event:** `evt-order-call-for-response-disposition` (cert stage, `response-requested` moment)  
**Input Snapshot:** `2026-08-14.json` (`cutoff`: `2026-08-15`, `sal-v4` band: `baseline`)  
**Forecast:** `denied` (`granted: false`, `probability: 0.08`)

---

## 1. Base-Rate Anchor (`metrics/statpack.md`)

From `record/context.json`, the frozen conditioning context at the `response-requested` moment (`opened_at: 2026-08-14`, `cutoff: 2026-08-15`) places this paid petition in the **`baseline`** salience band under `sal-v4` (`distribution_count: 1`, `cvsg_date: null`, private corporate petitioner).

Consulting `metrics/statpack.md` (Per-Term Salience-Band Grant Rates (`sal-v4`), strictly prior Terms OT2017–OT2025, 10-Term lookback window):
- Across OT2017–OT2025, the `baseline` band has **7,940.0** weighted resolved petitions and **363.0** risk-set grants, yielding a pooled strictly-prior **risk-set grant rate of 4.57%** (363 / 7,940).
- Recent single-Term risk-set grant rates in the `baseline` band are similar: 4.5% in OT2025 (42/940, partially censored), 3.3% in OT2024 (28/840), 4.8% in OT2023 (40/837), and 3.8% in OT2022 (32/841).
- In the pack-wide escalation breakdown, petitions with 0 relists (1 distribution) have an overall grant rate of ~1.7%, whereas petitions where the Court calls for a response (CFR) after a waiver historically grant at roughly 8–12% overall when well-postured, or ~5–9% when factoring in vehicle quality before the brief in opposition is filed.

Starting from the **4.57%** `sal-v4` `baseline` risk-set base rate, I adjust upward to **8.0% (`0.08`)** to reflect the positive signal of the Court's August 14, 2026 Call for Response (following Respondent's July 21, 2026 waiver) and top-tier Supreme Court Bar representation (Mayer Brown LLP: Andrew J. Pincus, Archis A. Parasharami, Daniel E. Jones), offset by severe procedural, finality, and vehicle obstacles embedded in the state-court posture.

---

## 2. Case Posture and Doctrinal Analysis

### A. The Substantive Issue: Post-*Mallory* "Consent by Registration" in Georgia
Petitioner Samsung Electronics America, Inc. (SEA)—a New York corporation headquartered in New Jersey—was sued in the State Court of Fulton County, Georgia by Respondent Jordan Brewer, a Texas resident injured in Texas when an allegedly counterfeit lithium-ion battery cell caught fire in his e-cigarette device. There is no specific personal jurisdiction in Georgia, and Georgia is neither SEA's state of incorporation nor its principal place of business.

Georgia is one of a tiny handful of states that treat general corporate registration to do business as consent to general personal jurisdiction over any claim arising anywhere in the world. Unlike Pennsylvania's statute upheld in *Mallory v. Norfolk Southern Railway Co.*, 600 U.S. 122 (2023) (42 Pa. Cons. Stat. § 5301(a)(2)(i)), which explicitly states that qualification as a foreign corporation enables Pennsylvania courts to exercise general personal jurisdiction, Georgia's foreign-corporation statutes (O.C.G.A. §§ 14-2-1501, 14-2-1505(b)) contain no mention of general personal jurisdiction. Instead, under *Allstate Insurance Co. v. Klein*, 262 Ga. 599 (1992), and *Cooper Tire & Rubber Co. v. McCall*, 312 Ga. 422 (2021), cert. denied, 142 S. Ct. 2000 (2022), the Georgia Supreme Court construes the definition of "foreign corporation" alongside its general long-arm statute to subject registered corporations to general jurisdiction, reasoning that *Klein* itself puts corporations on "notice" of this consequence.

Samsung raises two arguments tailored to *Mallory*:
1. **Lack of Statutory Notice:** In *Mallory*, Justice Jackson's opinion and the plurality emphasized that Pennsylvania's statute explicitly notified foreign corporations that registration entailed consent to general jurisdiction. Georgia's statutory text says nothing of the sort; it relies on judicial decisions (*Klein* and *Cooper Tire*).
2. **Retroactive Notice Problem:** SEA registered to do business in Georgia in **January 1989**—nearly four years *before* the Georgia Supreme Court decided *Klein* in November 1992. Thus, at the time SEA registered, not even judicial notice existed, and Georgia imposes perpetual general jurisdiction unless SEA withdraws from the Georgia market.

### B. Why Certiorari Is Still Unlikely Despite the Call for Response
While at least one Justice's chambers flagged the petition for a response—unsurprising given the ongoing interest in the boundaries of *Mallory* and Justice Alito's concurrence in *Mallory* questioning the validity of coerced registration regimes—this case suffers from multiple threshold and vehicle flaws that Respondent's Brief in Opposition will heavily exploit:

1. **Interlocutory Posture and 28 U.S.C. § 1257(a) Finality Questions:**
   The litigation in the State Court of Fulton County is ongoing in pre-trial discovery. The trial court denied SEA's motion to set aside earlier discovery and personal-jurisdiction rulings (relying on its discretionary "end of the term of court" plenary authority under Georgia law) and certified the order for immediate review. Both the Georgia Court of Appeals (Nov. 14, 2025) and the Georgia Supreme Court (Mar. 3, 2026) **denied discretionary/interlocutory review without opinion**.
   To satisfy 28 U.S.C. § 1257(a), Samsung must invoke the fourth *Cox Broadcasting Corp. v. Cohn*, 420 U.S. 469, 482–83 (1975) exception (following *Goodyear Dunlop Tires Operations, S.A. v. Brown*, 564 U.S. 915, 922 (2011), and *Shaffer v. Heitner*, 433 U.S. 186, 195 n.12 (1977)). However, here the Georgia appellate courts did not affirm a jurisdictional holding on the merits; they exercised discretion to deny interlocutory review of a trial court's refusal to set aside prior orders entered in an earlier term of court.

2. **Independent and Adequate State Procedural Grounds / Waiver in the Trial Court:**
   The trial court's July 30, 2025 order (Pet. App. 5a–6a) and October 7, 2025 order denying the motion to set aside (Pet. App. 3a–4a) rest heavily on state-law procedural waiver and term-of-court finality:
   - In its July 30, 2025 order, the trial court ruled that SEA "previously waived any objection to personal jurisdiction in its Motion for Protective Order" (Pet. App. 6a n.1) before raising *Mallory* only in a reply brief.
   - When SEA moved to set aside that ruling, the trial court held in its October 7, 2025 order that under Georgia law (`O.C.G.A. § 15-1-3(6)` and *Moon v. State*), a trial court's plenary power to revise or vacate its orders expires at the end of the two-month term of court in which the order was entered, unless the motion was filed within the term and pertained to the initial merits rather than a discovery motion.
   - Although the trial court added a footnote stating `See also Cooper Tire` (Pet. App. 4a n.2), the primary basis for denying the motion to set aside was Georgia's term-of-court procedural bar and SEA's earlier waiver of its personal-jurisdiction objection in discovery practice. Respondent's BIO will argue with considerable force that this case is entangled in state-law waiver and term-of-court rules, making it a poor vehicle to reach the federal *Mallory* question.

3. **Unreasoned Discretionary Denials Below and Recent Denials of Certiorari:**
   Neither the Georgia Court of Appeals nor the Georgia Supreme Court issued a reasoned opinion addressing Samsung's 1989 pre-*Klein* registration argument. Moreover, the Supreme Court denied certiorari in *Cooper Tire* itself (2022) and in post-*Mallory* challenges to *Cooper Tire* (such as *Pirelli Tire LLC v. Walters*, 145 S. Ct. 146 (2024)). And because Georgia's judicial implied-consent rule is nearly unique after *Mallory* (most other states having rejected implied consent by registration as a matter of state statutory interpretation), the split is lopsided and confined to Georgia.

Balancing the CFR signal and experienced counsel against these substantial vehicle defects, I place the probability of a grant (including GVR) at **0.08** (`predicted_disposition: "denied"`).

---

## 3. Mechanical Claims (`cert-v3`)

1. **`disposition` (`0.08`):** Matches headline `probability` (`0.08`).
2. **`relist-increment` (`0.98`):** Under `cert-v3`, this claim is vacuously masked on `evt-order-call-for-response-disposition` because a petition on which the Court calls for a response after initial distribution (`distribution_count: 1`) will be re-distributed for conference once the response is filed (save for a rare Rule 46 dismissal or withdrawal before re-distribution). I state `0.98` to reflect the near-certainty of at least one post-response distribution.
3. **`cvsg-increment` (`0.02`):** A CVSG on a Fourteenth Amendment personal-jurisdiction dispute arising from state-court products liability litigation is very rare (and the SG already participated as amicus in *Mallory*). Probability is set at `0.02`.
4. **`summary-disposition-route` (`0.15`):** Conditional on a grant (`P(summary | grant)`), the prior-Term paid summary-route base rate is ~0.354, but here the Court has no intervening precedent under which to GVR (since *Mallory* was decided in 2023 before the orders below) and a summary reversal on a novel post-*Mallory* constitutional question entangled in state procedural bars is unlikely. If the Court grants at all, it is ~85% likely to set the case for plenary briefing and argument (`0.15` conditional summary-route probability).
5. **`dissent-from-denial` (`0.04`):** Conditional on a denial (`P(noted dissent | denial)`), there is a modest chance (~4%) that a Justice who dissented in *Mallory* (e.g., Justice Alito, Barrett, Roberts, or Kagan) or who objects to consent-by-registration without explicit statutory notice notes a dissent or statement respecting the denial of certiorari, though the procedural vehicle flaws make a separate writing less likely than in a clean vehicle.
6. **`order-writers` distribution:** Per-Justice probabilities of writing on the cert order reflect small probabilities concentrated in Justices Alito (`0.025`), Gorsuch (`0.020`), and Thomas (`0.015`), who most frequently author separate statements or dissents at the cert stage, with minimal probabilities (`0.002`–`0.005`) for the remaining Justices.

---

## 4. Stakes (`big_case_score`) and Topic (`qp_topics`)

- **`big_case_score` (`0.42`):** If decided on the merits, the case would clarify a significant open question left by *Mallory v. Norfolk Southern Railway Co.*—whether a state may subject every registered foreign corporation to general personal jurisdiction without explicit statutory text, and whether pre-notice registration can bind a corporation perpetually. That question is important to nationwide corporate litigation and forum shopping in Georgia, placing the stakes well above routine cert petitions (`0.42`).
- **`qp_topics`:** Primary topic is `civil-procedure` (personal jurisdiction under the Fourteenth Amendment Due Process Clause), with `secondary: null` and `vehicle: false`.
