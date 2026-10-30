# Prediction Reasoning: *Genesis Financial Solutions, Inc. v. Steve Ford, et al.* (No. 25-311)

**Event:** `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`)  
**Input Snapshot:** `data/cases/scotus/73277388/record/snapshots/2025-11-07.json` (Cutoff: `2025-11-07`)

---

## 1. Base-Rate Anchor (`metrics/statpack.md`)

Per `record/context.json`, this cell is at the `response-requested` moment (`cutoff: 2025-11-07`, `term: 2025`, `salience_version: sal-v4`), with `band: "baseline"` (`distribution_count: 1`, `cvsg_date: null`, private petitioner).

From `metrics/statpack.md` (**Segment base rate by salience band (`sal-v4`)**), pooling the `baseline` risk-set (`[reached ...]`) rates across the October Terms strictly preceding `term: 2025` (OT2017–OT2024):
- **OT2024:** 5.9% ($n = 1274$, $\approx 75.2$ grants)
- **OT2023:** 5.9% ($n = 1312$, $\approx 77.4$ grants)
- **OT2022:** 5.9% ($n = 1196$, $\approx 70.6$ grants)
- **OT2021:** 5.7% ($n = 1500$, $\approx 85.5$ grants)
- **OT2020:** 4.5% ($n = 1740$, $\approx 78.3$ grants)
- **OT2019:** 4.7% ($n = 1399$, $\approx 65.8$ grants)
- **OT2018:** 4.8% ($n = 1529$, $\approx 73.4$ grants)
- **OT2017:** 4.9% ($n = 1649$, $\approx 80.8$ grants)

Across all $N = 11,599$ weighted resolved petitions in the strictly prior `baseline` risk set (OT2017–OT2024), the pooled grant-family rate is **5.23%** ($\approx 607.0 / 11,599$; terminal `baseline` rate is **1.30%** over $n = 8,780$). For originating circuit `ca4`, the modern paid discretionary-cert grant-family rate in the statpack is **2.5%** (1.3% granted + 1.2% GVR, 95.3% denied, 2.2% dismissed). With 1 cert-stage amicus brief (American Bankers Association), the marginal paid-segment grant-family rate is **15.1%** (10.3% granted + 4.8% GVR).

---

## 2. Case Posture & Docket Signals as of November 7, 2025

1. **Procedural Posture:** Respondent Steve Ford brought a putative class action in Maryland state court alleging that Genesis Financial Solutions, Inc. and Spring Oaks Capital SPV, LLC violated the Maryland Credit Service Business Act and Maryland Consumer Loan Law by marketing and collecting on credit-card loans issued through First Electronic Bank without Maryland licenses. Defendants removed to the District of Maryland and moved to compel arbitration.
2. **Decisions Below:** Judge Boardman (D. Md., 726 F. Supp. 3d 441) denied the motion to compel arbitration. Applying Maryland contract-formation law (*Cheek v. United Healthcare of the Mid-Atlantic, Inc.*, 835 A.2d 656 (Md. 2003), and *Harby ex rel. Brooks v. Wachovia Bank, N.A.*, 915 A.2d 462 (Md. App. Ct. 2007)), the district court held that an arbitration clause must be supported by independent mutual promises to arbitrate, and that the Credit Agreement's unilateral "Change of Terms" clause ("Subject to the limitations of applicable law, we may, at any time, change or remove any of the terms and conditions of, or add new terms and conditions to, this Agreement") rendered Defendants' promise to arbitrate illusory—whether "applicable law" meant Maryland law or federal/Utah law. The district court also noted in a footnote that the Fourth Circuit had previously held in *Noohi v. Toll Bros., Inc.*, 708 F.3d 599, 612 (4th Cir. 2013), that the FAA does not preempt *Cheek*.
3. **Fourth Circuit Affirmance:** On May 30, 2025, the Fourth Circuit (Wilkinson, Niemeyer, Wynn, JJ.) affirmed in a brief unpublished per curiam opinion without oral argument, relying on its published decision in *Johnson v. Continental Finance Co.*, 131 F.4th 169 (4th Cir. 2025), and citing *Noohi* in a footnote to reject the FAA preemption argument. Rehearing en banc was denied as untimely on June 17, 2025.
4. **Supreme Court Docket Activity (up to `2025-11-07`):**
   - Represented by Sidley Austin LLP (Collin P. Wedel), Petitioner filed its cert petition on September 15, 2025.
   - Respondent Steve Ford attempted to waive a response twice (September 16 and 19, 2025, not accepted for filing) and did not file a response by the October 17, 2025 due date.
   - Co-defendant/Respondent Spring Oaks Capital SPV, LLC filed a Rule 12.6 letter supporting certiorari on October 8, 2025.
   - The American Bankers Association (represented by Robert Mark Loeb, Orrick) filed an amicus brief supporting Petitioner on October 17, 2025.
   - Distributed on October 29, 2025 for the Conference of November 14, 2025 (`distribution_count: 1`).
   - On November 6, 2025, the Court requested a response (due December 8, 2025).

---

## 3. Legal Merits, Circuit Split, and Vehicle Analysis

### Strengths Supporting Certiorari
- **Capable Counsel & Institutional Amicus Support:** The petition is litigated by Sidley Austin and supported at the cert stage by the American Bankers Association (Orrick), highlighting the practical impact on standard-form credit-card agreements.
- **Call for a Response (CFR):** After Respondent Ford declined to respond, at least one Justice requested a response before the November 14 Conference. A CFR moves a petition out of the automatic-denial bucket of waived petitions and raises the conditional grant rate above the raw `baseline` risk-set average (5.23%).
- **FAA Equal-Treatment Tension:** Under *Kindred Nursing Centers Ltd. v. Clark*, 581 U.S. 246 (2017), and *AT&T Mobility LLC v. Concepcion*, 563 U.S. 333 (2011), state rules that single out arbitration clauses for disfavored treatment are preempted by FAA § 2. Petitioner argues that Maryland's *Cheek* rule requires independent consideration (mutual promises to arbitrate) solely for arbitration clauses within an otherwise valid contract supported by consideration, conflicting with decisions from the First, Second, Third, Sixth, and Eighth Circuits (*Soto*, *Doctor's Associates v. Distajo*, *Harris*, *Wilson Electric*, *Barker*).

### Vehicle Defects and Headwinds Against Certiorari
- **Unpublished, Two-Paragraph Per Curiam Below:** The Fourth Circuit decided this case in a two-paragraph unpublished opinion without oral argument, expressly piggybacking on the published opinion in *Johnson v. Continental Finance Co.*, 131 F.4th 169 (4th Cir. 2025), and relegating the FAA preemption issue to a single sentence in a footnote citing *Noohi* (2013). The Supreme Court is generally reluctant to grant plenary review to an unpublished summary affirmance when the underlying doctrine was announced in earlier published decisions (*Noohi* in 2013, for which cert was not granted, and *Johnson* in 2025).
- **Framing as Ordinary Illusory-Promise / Contract-Formation Doctrine:** Respondent Ford will forcefully argue in the Brief in Opposition that the decision below does not rest on an arbitration-specific hostility rule, but rather on standard state-law contract-formation principles governing illusory promises and unilateral modification clauses—principles that other circuits (including the Fifth, Seventh, and Tenth Circuits in cases like *Morrison v. Amway Corp.* and *Hardin v. First Cash Financial Services*) also apply when an unrestricted change-in-terms clause allows one party to unilaterally revoke or alter the agreement to arbitrate at any time.
- **Alternative Contract-Specific Issues Below:** The district court's 30-page opinion turned heavily on intricate, contract-specific questions of choice-of-law (whether Utah law applied to formation) and statutory interpretation of the Truth in Lending Act (Regulation Z) and the Utah Statute of Frauds (Utah Code Ann. § 25-5-4). Furthermore, Genesis itself was not the named counterparty ("we" was defined as First Electronic Bank), and the Fourth Circuit denied rehearing en banc as *untimely*.
- **Rule 46 Settlement / Dismissal Risk:** In consumer debt-collection class actions where an individual named plaintiff challenges a motion to compel arbitration and the Supreme Court calls for a response, there is also a non-trivial probability of a bilateral settlement and Rule 46 dismissal prior to or after briefing.

*(Disclosure Note: During `fedcourts query` retrieval, a docket-number lookup for `25-34`—the companion *Johnson v. Continental Finance Co.* petition cited on page 1 of the petition—was executed with `--decided-before 0` after `--decided-before 2025-11-07` returned no row because `--docket-number` suppresses open or later-decided dockets under a replay clock. That lookup returned the corpus row for `scotus/73272764` showing `date_decided: 2026-05-07, disposition: dismissed`. That post-cutoff fact is disclosed in `flags.json` under `leakage-disclosure` and is strictly excluded from and unused in this forecast, which is grounded solely on the pre-cutoff record as of November 7, 2025.)*

---

## 4. Synthesis and Probability Calibration

- **Base Rate Starting Point:** 5.23% (`sal-v4` `baseline` risk-set rate across OT2017–OT2024).
- **Upward Adjustments:** Call for a Response (+4%), strong Supreme Court counsel (Sidley Austin) and cert-stage amicus brief from the American Bankers Association (+3%), and the Court's historical interest in FAA § 2 preemption (+2%).
- **Downward Adjustments:** Unpublished two-paragraph per curiam opinion below with an untimely en banc petition (-3%), strong BIO argument that the case turns on fact-bound unilateral change-in-terms contract language rather than a clean circuit split (-3%).
- **Final Grant Probability:** **0.08** (8.0%), with `granted: false` and `predicted_disposition: "denied"`.

---

## 5. Declared Claims (`cert-v3`) and Distribution Claims

1. **`disposition` (0.08):** Matches top-level `probability` (8.0% chance of a grant or GVR/summary disposition).
2. **`relist-increment` (0.88):** As of the `2025-11-07` snapshot, `distribution_count` is `1` (from the October 29, 2025 distribution for the November 14, 2025 Conference). Because the Court requested a response on November 6, 2025 (with a due date of December 8, 2025), the petition will be taken off the November 14, 2025 Conference and redistributed for a subsequent Conference after the Brief in Opposition is filed (yielding `distribution_count >= 2`), unless the parties settle and dismiss the petition under Rule 46 before redistribution. (Note: `relist-increment` is moment-vacuous on `response-requested` cells, so the harness masks it at scoring, but the probability is stated as required.)
3. **`cvsg-increment` (0.01):** A Call for the Views of the Solicitor General is exceedingly rare in private FAA § 2 state-law contract-formation disputes that do not implicate a federal statute administered by an executive agency.
4. **`summary-disposition-route` (0.20):** Conditional on `granted = true`, most FAA § 2 preemption grants proceed to plenary review (80%), though a summary reversal or GVR in the cert order itself remains a 20% conditional possibility given the Court's past summary-reversal practice under the FAA.
5. **`dissent-from-denial` (0.02):** Conditional on denial, the vast majority of FAA commercial contract petitions are denied without a noted dissent or statement, especially where the Fourth Circuit opinion below is a two-paragraph unpublished per curiam affirmance. I assign 2.0%.
6. **`order-writers` (`claim_distributions`):** Consistent with the 2.0% `dissent-from-denial` estimate, per-Justice writing probabilities are very low, weighted slightly higher for Justices Thomas (0.008), Gorsuch (0.006), and Alito (0.005).

