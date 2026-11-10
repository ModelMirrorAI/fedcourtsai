# Certiorari Prediction Rationale: *Morrisey v. Jonathan R.* (No. 26-297)

- **Case ID:** `scotus/9026000297`
- **Event ID:** `evt-order-call-for-response-disposition` (`moment: response-requested`)
- **Snapshot Read:** `2026-10-19.json`
- **Forecast:** `predicted_disposition: "denied"`, `granted: 0`, `probability: 0.18`

---

## 1. Base-Rate Anchoring (`state` Band)

From `record/context.json`, this cell runs in `forward` mode with `band: "state"`, `salience_version: "sal-v8"`, `distribution_count: 1`, and `term: 2026`. The harness-frozen `cert_anchor` in `record/context.json` (matching the bracketed `reached` rate for the `state` band in `metrics/statpack.md` under **"Segment base rate by salience band (sal-v8)"**, pooled over the rendered Terms strictly preceding OT 2026, i.e., OT 2017–OT 2025, `n = 420` weighted resolved petitions) is **`0.2333` (23.3%)**.

Additional statpack cuts from `metrics/statpack.md` provide structural context:
- **Salience band terminal cut (`state`):** Over `n = 315` resolved petitions ending in the `state` band (without relisting into `high`), the breakdown is `denied 80.0%, granted 9.8%, gvr 8.3%, dismissed 1.9%` (18.1% grant family), while those reaching the `state` risk set overall grant at **23.3%** once subsequent relists into `high` are included.
- **Originating circuit (`ca4`):** Modern discretionary-cert petitions from the Fourth Circuit (`n = 3,425` resolved) resolve at `denied 95.2%, dismissed 2.2%, gvr 1.4%, granted 1.2%` (2.6% grant family).
- **Amicus count (`0`):** Paid scored-segment petitions with zero cert-stage amicus briefs (`n = 11,109` resolved) resolve at `denied 95.0%, granted 2.0%, gvr 1.8%, dismissed 1.3%` (though this cut is read at disposition and this petition is only at the CFR stage).

Anchoring on the **23.3%** `state` band `reached` rate, I adjust modestly downward to **0.18 (18%)** based on the provisioned filings (`petition.txt`, `questions-presented.txt`, `appendix.txt`, `decision-below.txt`, and `lower-court-docket.txt`) and corpus priors.

---

## 2. What in the Record Drives the Adjustment

### A. Why the Call for a Response Is a Modest Positive Signal Here
Respondents initially waived a response on October 6, 2026, and the Court called for a response on October 19, 2026 after the initial October 7 distribution. When a State Solicitor General petitions from a published circuit decision reversing a judgment in the State's favor—and accompanied by a 15-page partial dissent from Judge Rushing—a Call for a Response after a respondent waiver is routine. Because the Brief in Opposition has not yet been filed (due November 18, 2026), the Court has heard only Petitioners' framing and has not yet seen Respondents' vehicle arguments.

### B. Severe Vehicle & Prematurity Defects on Question 1
Petitioners' lead question asks whether Article III empowers a federal court to act as the "manager or policy planner" of a state agency, invoking *Trump v. CASA, Inc.*, 606 U.S. 831 (2025), and *Horne v. Flores*, 557 U.S. 433 (2009), to argue that comprehensive institutional-reform injunctions over state foster-care systems exceed traditional equitable authority.

However, as `decision-below.txt` (matching `appendix.txt` at App. 1a–57a) demonstrates:
1. **No Injunction and No Liability Finding Exist:** Two months before the scheduled trial and while West Virginia's summary judgment motion was pending, the district court *sua sponte* dismissed the entire lawsuit for lack of Article III standing (redressability) under Rule 12(h)(3), concluding that Plaintiffs' 47 remedial requests would require the court to manage West Virginia's foster-care system.
2. **Unanimous 3–0 Reversal on Question 1:** All three judges on the Fourth Circuit panel—Senior Judge Floyd, Judge Harris, and Judge Rushing—agreed that the standing dismissal had to be reversed. Judge Rushing's separate opinion (App. 43a–46a) explains why Question 1 is premature: at the threshold standing stage, "[a]t least some of the injunctive relief Plaintiffs seek is within the district court's authority and would relieve at least part of Plaintiffs' injuries. For our purposes, that is sufficient to show redressability." (App. 44a). If Plaintiffs eventually prove a constitutional or statutory violation at trial, "the district court can and should take these concerns into account when it comes time to fashion injunctive relief tailored to remedying those specific violations." (App. 46a).
3. **No Circuit Split and Prior Denials in the Corpus:** Every circuit to address similar foster-care lawsuits has allowed them to proceed past threshold standing (*B.K. ex rel. Tinsley v. Snyder*, 922 F.3d 957 (9th Cir. 2019); *M.D. ex rel. Stukenberg v. Abbott*, 907 F.3d 237 (5th Cir. 2018)). Corpus queries confirm that this Court previously denied certiorari in the first interlocutory appeal in this very case (*Justice v. Jonathan R.*, No. 22-240, cert. denied Oct. 11, 2022) as well as in the institutional-reform petitions Petitioners cite (*Faust v. B.K.*, No. 19-765, cert. denied Mar. 23, 2020; *Sault Ste. Marie Tribe v. Michigan*, No. 25-165, cert. denied Jan. 12, 2026).

### C. Strengths and Weaknesses of Question 2 (Conditional Cross-Appeal of Class Certification)
Question 2 is the main driver of grant risk. The Fourth Circuit majority held that once its reversal of the standing dismissal eliminated the final judgment and remanded the case for further proceedings, West Virginia's conditional cross-appeal of the 2023 class-certification order became "effectively interlocutory and thus unreviewable" outside Rule 23(f)'s 14-day window (App. 39a–42a). Judge Rushing dissented (App. 46a–57a), arguing that the class-certification order merged into the final judgment under 28 U.S.C. § 1291, that reversing on the main appeal activates rather than moots a conditional cross-appeal, that Rule 23(f) is nonjurisdictional under *Nutraceutical Corp. v. Lambert*, 586 U.S. 188 (2019), and that Plaintiffs forfeited any Rule 23(f) objection.

While Judge Rushing's dissent gives Question 2 real traction (both for a potential grant and for a ~3–4% chance of a summary vacatur/GVR), three considerations temper the grant probability:
1. **Unusual Procedural Posture:** West Virginia did not seek timely Rule 23(f) review when the class was certified in 2023. It obtained an appealable "final judgment" before trial only because the district court *sua sponte* and erroneously dismissed the suit for lack of standing right before trial. Reviewing class certification now would reward a defendant with interlocutory class review solely because of a district court's threshold error, whereas on remand West Virginia can still move to decertify or modify the class under Rule 23(c)(1)(C) or appeal after a genuine final judgment on the merits.
2. **Discretionary Nature of the Asserted Split:** Most of the circuit cases cited on the conditional cross-appeal question (*Blake v. City of Los Angeles*, 595 F.2d 1367 (9th Cir. 1979); *Milan Express Co. v. Western Surety Co.*, 886 F.2d 783 (6th Cir. 1989); *Fink v. Nat'l Sav. & Tr. Co.*, 772 F.2d 951 (D.C. Cir. 1985); *Council 31, AFSCME v. Ward*, 978 F.2d 373 (7th Cir. 1992)) predate Rule 23(f) (enacted in 1998), and as Judge Rushing herself recognized (App. 51a–52a), appellate courts have *discretion* whether to decide a conditional cross-appeal of an interlocutory order when reversing a pre-trial dismissal or leave it for the district court on remand.
3. **No En Banc Petition or Cert-Stage Amici:** `lower-court-docket.txt` confirms that West Virginia did not petition for rehearing en banc in the Fourth Circuit, and the snapshot shows zero cert-stage amicus briefs filed in this Court (`record/same-question.json` also shows no pending same-question petitions).

---

## 3. Uncertainties & Secondary Claims Calibration

- **Main Uncertainty:** How strongly the Brief in Opposition (not yet filed at this moment) exploits the pre-trial posture and whether any state amici file before conference, or whether several Justices view Judge Rushing's dissent on Question 2 and the Rule 23(b)(2) foster-care class certification analysis as warranting intervention (either plenary or via a narrow GVR/summary vacatur on Question 2).
- **Declared Claims:**
  - `disposition`: `0.18` (14.4% plenary grant + 3.6% GVR/summary reversal).
  - `relist-increment`: `0.98` (because the Court called for a response on October 19, the petition will almost certainly be distributed at least once more after the response is filed).
  - `cvsg-increment`: `0.02` (state foster-care litigation with no federal party or distinct federal agency interest).
  - `summary-disposition-route`: `0.20` (conditional on a grant, roughly a 1-in-5 chance that the Court vacates/remands in the cert order itself on Question 2's *sua sponte* Rule 23(f) holding rather than setting the case for oral argument).
  - `dissent-from-denial`: `0.10` (conditional on denial, a 10% chance that Justice Thomas, Justice Alito, or Justice Gorsuch writes a dissent or statement respecting denial on structural injunctions or Rule 23(b)(2) class certification).
- **`big_case_score` (`0.72`):** If decided on the merits, this case would be high-stakes: Question 1 implicates the viability of federal structural-reform injunctions over state institutions nationwide in the wake of *Trump v. CASA, Inc.*, and Question 2 governs appellate review of class certification on cross-appeal from a final judgment.
