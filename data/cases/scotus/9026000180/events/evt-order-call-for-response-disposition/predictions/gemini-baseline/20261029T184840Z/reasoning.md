# Certiorari Prediction: *Hudacko v. Regents of the University of California, et al.* (No. 26-180)

- **Case ID**: `scotus/9026000180`
- **Event ID**: `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`)
- **Input Snapshot**: `record/snapshots/2026-09-18.json` (cutoff `2026-09-18`, `mode: forward`)
- **Predicted Disposition**: `denied` (`P(denied) = 0.900`, `P(granted) = 0.070`, `P(gvr) = 0.015`, `P(dismissed) = 0.015`; overall grant-family `probability = 0.085`)

---

## 1. Base-Rate Anchor (`metrics/statpack.md`)

Under `record/context.json`, this paid Ninth Circuit petition enters at the `response-requested` moment in the **`baseline`** salience band (`sal-v4`), with `distribution_count = 1` (distributed on September 16, 2026 for the October 9, 2026 Long Conference, followed by a Call for a Response on September 17, 2026) and no CVSG.

From the committed corpus statpack (`metrics/statpack.md`):
- **Salience-band risk-set base rate (`sal-v4`)**: For a cell carrying a frozen `baseline` band at prediction time, skill is evaluated against the bracketed `[reached]` risk-set rate for `baseline` (all paid private-petitioner petitions that begin in `baseline`, including those that later escalate into `elevated` or `high` via relists or CVSG). Across completed Terms OT2017–OT2025, the `baseline [reached]` grant-family rate is **4.0% in OT2025** ($n = 1{,}314$) and **5.7%–5.9% in OT2021–OT2024** (multi-Term average $\approx 5.2\%$). Terminal `baseline` petitions that never accumulate relists grant at only **0.6%–1.9%**, whereas petitions that escalate to `elevated` grant at **7.8%–13.4%** terminally (`13.4%–20.8%` reached).
- **Originating circuit (`ca9`)**: Paid cert petitions from the Ninth Circuit resolve at `denied 94.8%, granted 2.1%, dismissed 1.9%, gvr 1.1%` (grant-family rate **3.2%**, $n = 5{,}577$).
- **Amicus support (`2+` cert amici)**: Paid petitions attracting 2 or more cert-stage amicus briefs have a marginal base rate of `denied 76.0%, granted 18.4%, gvr 4.5%, dismissed 1.2%` (grant-family rate **22.9%**, $n = 1{,}449$), though that marginal slice pools federal/state petitioners, CVSGs, and multi-relist cases.

Starting from the **4.0%–5.2%** `baseline [reached]` base rate and conditioning on the positive procedural signals observable at the September 18, 2026 cutoff (a Call for a Response after waivers plus five cert-stage amicus briefs), the appropriate starting prior before vehicle and merits adjustments is roughly **10%–14%** (typical of a private petition that has cleared the waiver screen via a CFR with organized amicus backing).

---

## 2. Case Background and Procedural Posture

In August 2020, following contested divorce and custody proceedings in Contra Costa County Superior Court, the family court awarded Petitioner Edward Hudacko's ex-wife (Respondent Christine Underhill) sole legal custody over their then-16-year-old child (`S.H.`), authorizing Underhill to "make decisions on her own for [Minor's] health, education and welfare without Father's consent" (Pet. App. 11a, 147a). Two specific provisions governed gender-related medical care:
- **Section 7a**: "[Minor] shall be permitted to pursue the services provided by UCSF as to the Minor Child's gender identity, and shall be permitted to commence hormone therapy, if recommended by UCSF." (Pet. App. 11a–12a.)
- **Section 7b**: "[Minor] will not be permitted to undergo any gender identity related surgery until they are 18 years of age, absent a written agreement by both parties, Christine Hudacko [Underhill] and Edward Hudacko, or an order of the court." (Pet. App. 12a.)

In August 2021, with Underhill's and the 17-year-old minor's consent (and UCSF's recommendation), UCSF physicians inserted a 3.5 cm subcutaneous Supprelin LA (histrelin acetate) puberty-blocker implant into the inner aspect of the minor's upper arm under local anesthesia, alongside oral estradiol (Pet. App. 12a, 192a–197a). After receiving an insurance explanation of benefits categorizing the implant insertion under a "surgery" billing code, Hudacko brought this action under 42 U.S.C. § 1983 and California tort law in the Northern District of California against UCSF physicians Drs. Stephen Rosenthal and Janet Yi Man Lee, UCSF psychologist Diane Ehrensaft, UCSF gender clinic legal director Asaf Orr, ex-wife Underhill, her family-law attorney Nathaniel Bigger, and court-appointed minor's counsel Daniel Harkins.

Judge Susan Illston dismissed the Second Amended Complaint under Rule 12(b)(6), holding that: (1) Underhill, Bigger, and Harkins were private actors, not de facto state actors; (2) the UCSF individual defendants were entitled to qualified immunity on the Fourteenth Amendment substantive due process claim because a reasonable official could view the hormone-releasing implant as permitted "hormone therapy" under Section 7a rather than prohibited "gender identity related surgery" under Section 7b; and (3) the state-law fraudulent concealment and emotional distress claims failed as a matter of California law (Pet. App. 10a–46a).

On October 21, 2025, a unanimous Ninth Circuit panel (Judges S.R. Thomas, Nguyen, and Bress) affirmed in a short, unpublished memorandum disposition (`2025 WL 2965766`, Pet. App. 1a–9a). On March 11, 2026, the Ninth Circuit denied panel rehearing and rehearing en banc; although one active judge requested a vote on rehearing en banc, the petition failed to receive a majority of votes and **no judge dissented from or wrote a statement respecting the denial of rehearing en banc** (`168 F.4th 1245`, Pet. App. 93a–94a).

After Justice Kagan granted a 59-day extension (`25A1345`), Hudacko—now represented by Gene C. Schaerr of Schaerr | Jaffe LLP—filed this petition on August 7, 2026, raising two Questions Presented:
1. Whether judicial decisions are the only valid source of "clearly established law" for qualified immunity (allegedly the rule in the 5th, 7th, 9th, 10th, and D.C. Circuits), or whether non-caselaw sources and non-legal materials such as professional knowledge may also be examined (allegedly the rule in the 1st, 2d, 3d, 4th, 6th, 8th, and 11th Circuits).
2. Whether qualified immunity's clearly-established-law test applies uniformly to all government officials, or requires a threshold historical inquiry into whether immunity was accorded to the relevant official at common law in 1871 (*citing Baxter v. Bracey*, 590 U.S. 1011, 1014 (2020) (Thomas, J., dissenting from denial of certiorari)).

All four respondent groups waived their right to respond between August 25 and September 3, 2026. Five amicus briefs supporting Petitioner were filed by NC Values Institute, Sutherland Institute, Independent Women's Law Center & Manhattan Institute, American College of Pediatricians, and Our Duty–USA et al. Following distribution on September 16, 2026 for the October 9, 2026 Conference, the Court called for a response on September 17, 2026 (due October 19, 2026).

---

## 3. Analysis of Certiorari Factors

### A. Factors Favoring Review (Why the Court Called for a Response)
1. **Call for a Response (CFR) and Amicus Mobilization**: The September 17, 2026 CFR demonstrates that at least one Justice's chambers flagged the petition rather than letting it be summarily denied on waivers at the Long Conference. Combined with five cert-stage amicus briefs and experienced Supreme Court counsel (Gene Schaerr), the petition has elevated visibility.
2. **Intersection of Two Themes Tracked by Conservative Justices**: The petition deliberately pairs two themes that several Justices have written separately about:
   - State interference with parental authority over minor gender transitions (*Parents Protecting Our Children, UA v. Eau Claire Area School District*, 145 S. Ct. 14 (2024) (Alito, J., joined by Thomas, J., dissenting from denial of certiorari; Kavanaugh, J., voting to grant); *Lee v. Poudre School District R-1*, 146 S. Ct. 26 (2025) (Alito, J., joined by Thomas and Gorsuch, JJ., statement respecting denial of certiorari); *Mirabelli v. Bonta*, 607 U.S. 492 (2026) (per curiam)).
   - Justice Thomas's longstanding criticism of modern qualified immunity's "one-size-fits-all" clearly-established-law standard detached from the 1871 common-law backdrop (*Baxter v. Bracey*, 590 U.S. 1011 (2020); *Hoggard v. Rhodes*, 141 S. Ct. 2421 (2021)).

### B. Factors Weighing Strongly Against Certiorari (Why Denial Remains Very Likely)
Once the UCSF Respondents (represented by WilmerHale's Michael Mongan) and the remaining Respondents file their Briefs in Opposition, several severe vehicle and merits obstacles will become unmistakable:

1. **Question 2 Was Concededly Forfeited Below**:
   Petitioner explicitly concedes that the second Question Presented—asking the Court to require a threshold 1871 common-law historical inquiry for qualified immunity and apply *Hope v. Pelzer* to state medical personnel—**was never raised in the district court or the Ninth Circuit** (Pet. 36: "Nor does it matter that the second question presented was not raised below—there is no need to futilely raise issues squarely foreclosed by this Court's precedent"). As "a court of review, not of first view," the Supreme Court almost never grants certiorari to overhaul a foundational § 1983 doctrine on an issue that was never briefed or passed upon below. Moreover, the Court has repeatedly declined invitations to revisit *Harlow v. Fitzgerald* in cleaner, preserved vehicles, and just this year applied its conventional qualified-immunity specificity standard in *Zorn v. Linton*, 146 S. Ct. 926 (2026) (per curiam).

2. **Question 1 Relies on a Manufactured Split That Does Not Fit the Decision Below**:
   Petitioner frames Question 1 as a 5–7 circuit split over whether internal policies, regulations, or professional standards can inform "clearly established law." That framing mischaracterizes what the Ninth Circuit actually decided:
   - First, the Ninth Circuit did not announce a categorical rule barring non-caselaw sources in qualified-immunity inquiries; its two-paragraph discussion is an **unpublished, non-precedential memorandum disposition** (`2025 WL 2965766`, Pet. App. 4a–5a).
   - Second, the circuit cases Petitioner cites on the "majority" side (e.g., *Cintron*, *Iko*, *Latits*, *Okin*) involve whether an official's violation of *constitutional* standards was obvious in light of department training or prison regulations that implement constitutional norms. Here, by contrast, Petitioner is not using medical literature or an insurance EOB to show that the *Fourteenth Amendment* prohibits a Supprelin implant; he is using a California optometry statute (`Cal. Bus. & Prof. Code § 3041`), a dictionary definition, an insurance billing code, and FDA package-insert instructions ("Insertion of the Supprelin LA implant is a surgical procedure") to argue how to construe the phrase **"any gender identity related surgery"** as opposed to **"hormone therapy, if recommended by UCSF"** in a *single state family-court custody order*.
   - Third, as the Ninth Circuit held (Pet. App. 5a, 7a–8a), the family-court order expressly authorized Underhill to consent to "hormone therapy, if recommended by UCSF," and the Supprelin LA implant is a subcutaneous GnRH-agonist drug-delivery implant that delivers hormone-blocking medication ("12 months of hormonal therapy," Pet. App. 196a). Whether a subcutaneous drug implant is classified as "hormone therapy" under Section 7a or "gender identity related surgery" under Section 7b of a Contra Costa County custody decree is an idiosyncratic question of state-court order interpretation, not a recurring question of federal constitutional law.
   - Fourth, the Ninth Circuit independently noted that "putting aside the custody order, Hudacko cites no clearly established law creating a parental liberty interest in precluding the procedure at issue here when the other parent and minor child consent to it" (Pet. App. 5a). Even in circuits that consider non-caselaw materials, neither an insurance billing code nor a drug label establishes a Fourteenth Amendment substantive due process right of a non-custodial parent to override the medical consent of the parent who holds sole legal and medical custody under a valid state-court decree.

3. **Poor Vehicle for Fourteen Amendment Parental-Rights Jurisprudence**:
   Unlike *Mirabelli v. Bonta*, 607 U.S. 492 (2026), *Parents Protecting*, or *Lee v. Poudre School District* (corpus prior `scotus/71639365`, No. 25-89, denied October 14, 2025 after 2 distributions), where fit parents holding full legal custody challenged public school policies that concealed their children's gender transitions from both parents, Hudacko's parental rights had already been adjudicated and restricted by a state family court after a contested custody hearing, and the child's mother—who held sole medical custody—actively consented to the treatment. Even in *Lee* (No. 25-89), which presented the parental-rights question far more cleanly without the complication of a state divorce custody decree or an unpreserved qualified-immunity overhaul, the Court denied certiorari. Furthermore, the absence of any dissent from the Ninth Circuit's denial of rehearing en banc (`168 F.4th 1245`)—despite an active judge calling for a vote—strongly suggests that even sympathetic Ninth Circuit judges recognized the case's vehicle flaws.

4. **Negligible GVR Prospect**:
   *Mirabelli v. Bonta*, 607 U.S. 492 (2026), was already decided before the petition was filed and is cited in the petition itself (Pet. 4–5), and Petitioner does not request a GVR. Because no pending Supreme Court merits case addresses either the interpretation of state custody orders in § 1983 suits or the threshold historical test for qualified immunity, a GVR is very unlikely (`1.5%`).

---

## 4. Conclusion and Probability Calibration

- **`denied` (`0.900`)**: Once the Brief in Opposition is filed (due October 19, 2026), the Court may relist the case once or twice if a Justice (such as Justice Thomas or Justice Alito) drafts a brief statement or dissent respecting the denial of certiorari, but the petition is overwhelmingly likely to be denied due to the unpublished below-court ruling, the fact-bound state custody-order dispute, the mother's sole medical custody and consent, and the forfeiture of Question 2 below.
- **`granted` (`0.070`)**: There is a small (~7.0%) chance that four Justices vote to grant certiorari—most plausibly limited to Question 1 or to address qualified immunity at the Rule 12(b)(6) stage—given the CFR, five amicus briefs, and four Justices' previously stated interest in parental-rights and qualified-immunity issues.
- **`gvr` (`0.015`)**: Very low probability (`1.5%`) of a summary disposition or GVR, as no intervening or pending Supreme Court authority controls the custody-order qualified-immunity issue here.
- **`dismissed` (`0.015`)**: Standard small allowance (`1.5%`) for Rule 46 or pre-disposition dismissal.
- **Overall `probability` (`granted` + `gvr` + `granted-in-part`)**: `0.085` (`8.5%`), hence `granted: false` and `predicted_disposition: "denied"`.
