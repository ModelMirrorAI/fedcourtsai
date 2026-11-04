# Prediction Reasoning: *Jesse Guardado v. Richard Comerford, Secretary, Florida Department of Corrections, et al.* (`26A634` / `scotus/9526000634`)

## 1. Executive Summary

- **Event**: `evt-motion-disposition` (`stage: interim`, `kind: motion`, `decision_target: disposition`, `moment: arrival`)
- **Application**: Emergency Application for a Stay of Execution (`No. 26A634`, linked with Petition for a Writ of Certiorari `No. 26-6051`), submitted to Justice Clarence Thomas on November 3, 2026, ahead of Applicant Jesse Guardado's scheduled execution on Thursday, November 5, 2026, at 6:00 p.m. EST.
- **Provisioned Inputs Read**:
  - Snapshot: `data/cases/scotus/9526000634/record/snapshots/2026-11-04.json` (`input_snapshot: "2026-11-04.json"`)
  - Context: `data/cases/scotus/9526000634/record/context.json` (`mode: "forward"`, `cutoff: "2026-11-04"`, `cut_kind: "arrival-position"`, `cut_anchor_index: 0`, `term: 2026`)
  - Documents: `data/cases/scotus/9526000634/record/documents/application.txt` (18 pages, `empty_text: false`, `truncated: false`) and `documents.json`
- **Prediction**: **Denied** (`granted: 0`, `predicted_disposition: "denied"`, `probability: 0.02`, `big_case_score: 0.18`).

---

## 2. Baseline and Interim-Docket Anchoring (`metrics/statpack.md` & `metrics/statpack.json`)

Under the predictor contract for an `interim` cell in `application_term = 2026` (`26A634`, prior to OT2027), the scored baseline yardstick is the substantive resolved slice's grant rate under the **finer reading** (`finer_granted` / `finer_resolved`), pooled over the ten strictly-prior application Terms (`2016 <= T < 2026`), subject to the pre-registered floor of **50** resolved substantive applications (`INTERIM_BASE_RATE_MIN_RESOLVED = 50`) and the requirement that every pooled Term carry `finer_unread == 0`.

1. **Finer-Reading Pool Inspection (`metrics/statpack.json`)**:
   In the committed `metrics/statpack.json` (`interim.by_term`), every Term from `2016` through `2025` currently records `finer_granted: 0`, `finer_resolved: 0`, and non-zero `finer_unread` (`226` in OT2025, `194` in OT2024, `149` in OT2023, `115` in OT2022, `189` in OT2021, `166` in OT2020, `137` in OT2019, `110` in OT2018, `56` in OT2017, and `83` in OT2016; `1,465` total unread across the pack). Because `finer_unread > 0` in every prior Term and the pooled `finer_resolved` count (`0`) does not clear the 50-application floor, **we anchor without a published finer-reading baseline** as required by the prompt contract when the finer-reading pool does not clear the floor. (Note also that the caption of the "The interim docket (applications)" section in `metrics/statpack.md` still carries the older descriptive-only phrasing while displaying `resolved (subst.)` and `granted` from the older registered `substantive_resolved` / `substantive_granted` columns.)

2. **Older Registered Substantive-Slice Shape (`metrics/statpack.md`)**:
   Without anchoring on the older registered reading `substantive_granted` / `substantive_resolved`, we note its shape as context: across the ten strictly-prior Terms (`OT2016`–`OT2025`), `substantive_granted / substantive_resolved` is `190 / 1,422` (`13.36%`), with `31 / 226` (`13.7%`) in OT2025 (`unparsed: 842`) and `38 / 194` (`19.6%`) in OT2024 (`unparsed: 752`). Across the pack's `1,465` substantive resolved applications (`192` granted, `13.1%`), grants are heavily concentrated in applications with terminal escalation signals (`109 / 391 = 27.9%` granted where `response_requested` fired; `132 / 403 = 32.8%` granted where `referred_to_court` fired) and in government or institutional emergency stay applications. At our arrival cut (`cut_anchor_index: 0`, `2026-11-04`), `context.json` shows `signals_observable: true`, `response_requested: false`, `referred_to_court: false`, and `amicus_briefs: 0`.

3. **Capital Execution-Stay Sub-Population**:
   Within the substantive stay stream (`1,297` stay applications in `statpack.md`), last-minute capital stay-of-execution applications filed by prisoners within days of a scheduled execution—especially those arising from method-of-execution challenges under 42 U.S.C. § 1983 after both a federal district court and a federal court of appeals have denied relief—are granted at a rate well below 2%.

---

## 3. Procedural Posture and Lower-Court Record

### A. Underlying Conviction and Warrant History
In 2005, Jesse Guardado pleaded guilty in Walton County Circuit Court, Florida, to the September 13, 2004 first-degree murder and armed robbery of 75-year-old Jackie Malone. Following a unanimous jury recommendation (`12-0`), he was sentenced to death.
- **Direct Appeal**: Affirmed in *Guardado v. State*, 965 So. 2d 108 (Fla. 2007), *cert. denied*, 552 U.S. 1197 (2008).
- **State Postconviction**: Denied in *Guardado v. State*, 176 So. 3d 886 (Fla. 2015), *Guardado v. Jones*, 226 So. 3d 213 (Fla. 2017), *cert. denied*, 584 U.S. 922 (2018), and *Guardado v. State*, 238 So. 3d 162 (Fla. 2018), *cert. denied*, 586 U.S. 1004 (2018).
- **Initial Federal Habeas**: Denied by the Northern District of Florida, affirmed by the Eleventh Circuit in *Guardado v. Secretary, Florida Department of Corrections*, 112 F.4th 958 (11th Cir. 2024), *cert. denied*, *Guardado v. Dixon*, 145 S. Ct. 2822 (2025).
- **Death Warrant & State Warrant Litigation**: On October 5, 2026, Governor Ron DeSantis signed a death warrant scheduling Guardado's execution for November 5, 2026, at 6:00 p.m. On October 29, 2026, the Florida Supreme Court unanimously affirmed the summary denial of Guardado's successive state postconviction motion and denied a stay of execution in *Guardado v. State*, No. SC2026-1605 (Fla. Oct. 29, 2026) (CourtListener Opinion ID `11516852`).

### B. The Federal § 1983 Method-of-Execution Action (`3:26-cv-02596` & `11th Cir. No. 26-14027`)
On September 28, 2026—one week before the Governor signed his death warrant—Guardado filed a pro se 42 U.S.C. § 1983 complaint in the U.S. District Court for the Middle District of Florida (`No. 3:26-cv-02596-MMH-SJH`, Judge Marcia Morales Howard) challenging Florida's three-drug lethal-injection protocol (200 mg etomidate, 1,000 mg rocuronium bromide, and 240 mEq potassium acetate). After the warrant was signed on October 5, 2026, the court appointed the Capital Habeas Unit of the Federal Public Defender for the Northern District of Florida (`CHU-N`), which filed a motion to stay execution on October 12, 2026, and an amended complaint on October 19, 2026.

Guardado alleged five ways in which the Florida Department of Corrections (FDOC) created a substantial risk of conscious suffocation and severe pain in violation of the Eighth Amendment (`application.txt` at 4–10):
1. FDOC's drug logs omitted any entry showing etomidate was withdrawn for three 2025 executions (Thomas Gudinas, Michael Bell, and Edward Zakrzewski);
2. Post-mortem whole-blood toxicology reports showed wide disparities in etomidate concentrations (e.g., 1.8 mg/L for Samuel Smithers vs. 0.18 mg/L for Michael Bell);
3. FDOC's drug logs recorded an expiration date of `01/31/2025` for etomidate used in six 2025 executions (Michael Tanzi, Glen Rogers, Anthony Wainwright, Samuel Smithers, Norman Grim, and Bryan Jennings), after which FDOC personnel used Wite-Out liquid eraser during litigation to overwrite the expiration dates without an audit trail;
4. FDOC's drug logs reflected lower withdrawn quantities of rocuronium bromide and potassium acetate in two executions (Wainwright and Gudinas); and
5. FDOC's drug logs showed withdrawals of lidocaine, an unlisted drug not named in the main three-drug sequence.

Judge Howard ordered limited discovery on the expired-etomidate allegations, reviewed unredacted pharmacy logs containing lot and invoice numbers *in camera*, and conducted a seven-hour evidentiary hearing on October 27, 2026, taking testimony from Guardado's two experts and FDOC's witnesses (including Chief of Pharmaceutical Services Dr. Renea Marcano and FDLE Agents Adam Graff and Kevin James). On October 30, 2026, the district court denied Guardado's motion for a stay of execution (`Doc. 59`).

On November 2, 2026, a unanimous panel of the Eleventh Circuit (Chief Judge William Pryor, Judge Jill Pryor, and Judge Luck) denied Guardado's motion for a stay of execution pending appeal (`No. 26-14027`, RECAP Doc. `13-1`, CourtListener Document ID `500108161`).

---

## 4. Assessment of Certworthiness and Stay Factors (`Hollingsworth v. Perry` & `Glossip v. Gross`)

To obtain a stay of execution pending certiorari under *Hollingsworth v. Perry*, 558 U.S. 183, 190 (2010), and *Hill v. McDonough*, 547 U.S. 573, 584 (2006), Guardado must show (1) a reasonable probability that four Justices will consider the issue sufficiently meritorious to grant certiorari; (2) a fair prospect that a majority of the Court will vote to reverse the judgment below; and (3) a likelihood that irreparable harm will result from the denial of a stay, alongside equitable considerations including timeliness.

Every prong weighs heavily against a stay:

### 1. Fact-Bound Clear-Error Review on *Glossip* Prong One ("Two-Court Rule")
Guardado's first question presented in `No. 26-6051` asks whether the lower courts clearly erred in crediting FDOC's witnesses over the face of FDOC's written drug logs. As both the Eleventh Circuit majority and Judge Jill Pryor's concurrence (`Order at 5–11; Concurrence at 2`) emphasized, the district court's factual findings are reviewed only for clear error (*Glossip v. Gross*, 576 U.S. 863, 881 (2015); *Cooper v. Harris*, 581 U.S. 285, 293 (2017)):
- **Expired Etomidate**: Dr. Marcano testified that a pharmacy employee for whom English was a second language mistakenly wrote the current year (`2025`) rather than the drug's expiration date (`January 2027`) on the log. Crucially, the district court verified from unredacted purchase receipts and lot numbers *in camera* that FDOC never possessed etomidate expiring on January 31, 2025, that the stock used in the 2025 executions had a January 2027 expiration date, that FDLE Agents Graff and James visually verified unexpired vials before administration in five of the six executions, and that Dr. Marcano personally set aside unexpired etomidate (expiring January 2027) for Guardado's execution.
- **Omitted Log Entries**: Although the pharmacy log omitted withdrawal entries for Gudinas, Bell, and Zakrzewski, Agent Graff testified that etomidate was administered, and post-execution toxicology reports undisputably proved etomidate was in all three prisoners' blood after their executions.
- **Post-Mortem Whole-Blood Disparities**: Both parties' medical experts acknowledged that post-mortem drug redistribution and metabolism make post-mortem whole-blood measurements taken hours after death unreliable proxies for live plasma concentrations during the execution.
- **Lidocaine**: Dr. Marcano and Agent Graff testified that lidocaine is a local anesthetic kept on the medical cart solely in the event a venous cutdown procedure (expressly referenced in the protocol) is needed, that FDOC has not performed a cutdown in years (none in the 13 executions witnessed by Agent Graff), and that there is no evidence Guardado will require one.

While Judge Jill Pryor wrote separately (`Concurrence at 1–4`) to condemn FDOC's sloppy recordkeeping and its "completely inappropriate" use of Wite-Out liquid eraser during litigation without documenting the alterations, she expressly joined Parts I, II.A, II.C, and IV of the panel order, concluding that "the recordkeeping failures in this case do not rise to the level of a constitutional tort" and that "based on the district court's fact findings, which are not clearly erroneous, Mr. Guardado is not entitled to a stay of his execution."

### 2. Independent Alternative Fatal Defect on *Glossip* / *Nance* Prong Two (Feasible Alternative Method)
Under *Glossip*, 576 U.S. at 877, *Bucklew v. Precythe*, 587 U.S. 119, 134 (2019), and *Nance v. Ward*, 597 U.S. 159, 164 (2022), a prisoner challenging a method of execution must also establish a feasible, readily implemented alternative method that significantly reduces a substantial risk of severe pain. In Part II.B (`Order at 11`), the Eleventh Circuit majority held that Guardado's stay motion on appeal was "silent on the second requirement"—never once mentioning a feasible alternative method of execution or explaining the omission—which "is fatal to a stay." Even in his Supreme Court stay application (`application.txt` at 11), Guardado merely asserts in a single sentence that he sufficiently pleaded a firing squad in his district court complaint (`Doc. 30`), without overcoming his forfeiture of that element in his Eleventh Circuit stay motion. This independent procedural defect makes certiorari review and reversal in `No. 26-6051` an exceptionally poor vehicle.

### 3. Independent Equitable Bar for Unnecessary Delay (*Hill v. McDonough* / *Nelson v. Campbell*)
In Part III (`Order at 13–15`), the Eleventh Circuit majority independently held that the "strong equitable presumption against the grant of a stay" (*Nelson v. Campbell*, 541 U.S. 637, 650 (2004); *Hill*, 547 U.S. at 584) barred relief because Guardado delayed 7 to 9 months after the same FDOC drug-log claims were raised by Frank Walls, Ronald Heath (*Heath v. State*, 426 So. 3d 1253 (Fla. 2026)), and Melvin Trotter (*Trotter v. State*, 428 So. 3d 68 (Fla. 2026)), despite having become warrant-eligible in 2025 when this Court denied certiorari in his federal habeas appeal (*Guardado v. Dixon*, 145 S. Ct. 2822 (2025)).

### 4. Abuse-of-Discretion Standard on Discovery Management (Question Presented 2)
Guardado's second question presented challenges the district court's case-management decisions limiting discovery to updated drug logs and holding a one-day evidentiary hearing. As the entire Eleventh Circuit panel held in Part II.C (`Order at 11–13`), district courts possess broad discretion over discovery, and here the district court ordered production of updated drug logs, inspected unredacted lot/invoice records *in camera*, and heard live testimony and cross-examination from both sides' expert and fact witnesses. A discretionary discovery ruling in a preliminary-injunction hearing does not present a circuit split or certworthy question.

### 5. Direct Precedent from Companion 2026 Florida Execution Stay Applications (*Trotter v. Florida*)
The Supreme Court has repeatedly denied stays of execution and certiorari in 2025 and 2026 Florida capital cases raising challenges to the etomidate protocol and FDOC's pharmacy logs, including *Trotter v. Florida*, 146 S. Ct. 755 (2026), *Gudinas v. Florida*, 145 S. Ct. 2833 (2025), *Bell v. Florida*, 145 S. Ct. 2872 (2025), and *Zakrzewski v. Florida*, 146 S. Ct. 57 (2025). In *Trotter*, Justice Sotomayor issued a statement respecting the denial of the application for stay of execution and denial of certiorari (146 S. Ct. at 756) highlighting concerns over FDOC's pharmacy log errors while not dissenting from the denial of a stay. Because Guardado subsequently received the very federal evidentiary hearing and *in camera* invoice/lot verification that had not occurred in state court in *Trotter*—and that evidentiary record refuted the claim that FDOC's etomidate was actually expired—there is even less basis for four Justices to grant certiorari or five Justices to grant a stay here.

---

## 5. Calibration of `probability`, `claims`, `claim_distributions`, and `big_case_score`

1. **Top-Level `probability` (`0.02`) and `interim-disposition` (`0.02`)**:
   Given the unanimous 3-0 Eleventh Circuit denial after a 7-hour federal evidentiary hearing and *in camera* verification of unredacted pharmacy records, the deferential clear-error standard of review, the two independent alternative grounds supporting denial (appellate forfeiture of *Glossip* Prong Two and *Hill* equitable delay), and the Court's prior denial in *Trotter v. Florida*, 146 S. Ct. 755 (2026), we set `probability = 0.02` (`granted = 0`, `predicted_disposition = "denied"`). The 2% tail risk accounts for the slim possibility of a temporary or administrative stay prompted by the evidentiary-hearing testimony that FDOC personnel altered official pharmacy logs with Wite-Out during active litigation.

2. **Escalation Ladder Claims (`interim-v3`)**:
   - `response-requested-increment: 0.15` — At arrival (`cut_anchor_index: 0`), `response_requested` is `false`. On the live docket on November 4, 2026, Respondent Richard Comerford submitted his response to the stay application directly (as is standard practice in active death-warrant cases) without a separate prior `Response requested` entry on the docket. We assign `0.15` for the modest chance that a separate call-for-response entry is nevertheless logged or parsed on the docket before resolution.
   - `referral-increment: 0.85` — At arrival, `referred_to_court` is `false`. In last-minute capital execution-stay applications submitted to Justice Thomas, standard practice is for the Circuit Justice to refer the application to the full Court, which then enters an order of the Court denying the stay (`"presented to Justice Thomas and by him referred to the Court is denied"`). We therefore assign `0.85`.
   - `amicus-increment: 0.04` — At arrival, `amicus_briefs` is `0`. Because the execution is scheduled for November 5, 2026 (within 48 hours of filing) and the dispute turns on case-specific evidentiary-hearing findings, we assign `0.04` to the chance that an amicus brief or motion is submitted on `26A634` before disposition.

3. **Order Writers (`order-writers` in `claim_distributions`)**:
   Most capital stay denials issue without separate writings, so most Justices carry very low writing probabilities (`Roberts: 0.005`, `Thomas: 0.01`, `Alito: 0.005`, `Gorsuch: 0.01`, `Kavanaugh: 0.01`, `Barrett: 0.01`, `Kagan: 0.03`). However, Justice Sotomayor (`0.22`) authored the statement respecting the denial of the stay and certiorari in *Trotter v. Florida*, 146 S. Ct. 755, 756 (2026), on the same FDOC drug-log controversy, and Judge Jill Pryor's concurrence below specifically invoked *Trotter* in spotlighting FDOC's use of Wite-Out on official logs during litigation. Justice Jackson (`0.12`) also writes or authors separate dissents/statements in capital cases at an elevated rate.

4. **Big Case Score (`big_case_score: 0.18`)**:
   While any capital execution-stay application involving allegations of altered state lethal-injection records attracts public and press scrutiny, if decided this application would turn on fact-bound clear-error review of a single evidentiary hearing and procedural preservation defects rather than establishing a broad new constitutional rule. We therefore score its significance if decided at `0.18`.
