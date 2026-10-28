# Rationale for Merits Prediction: *Department of the Air Force v. Prutehi Guahan* (No. 25-579)

**Event:** `evt-argument-judgment` (`stage: merits`, `moment: argued`)  
**Mode:** `forward` (`input_snapshot: "2026-10-08.json"`)  
**Summary of Forecast:** `granted: 1`, `probability: 0.90` (`judgment-disturbed`), `judgment: "reversed"`, `predicted_disposition: "other"`, `confidence: 0.85`, `big_case_score: 0.55`

---

## 1. Provisioned Inputs Consulted

I worked from the provisioned case-level record at `data/cases/scotus/73279024/record/` and the event definition at `data/cases/scotus/73279024/events/evt-argument-judgment/event.yaml`:
- **Snapshot & Conditioning:** `record/snapshots/2026-10-08.json` and `record/context.json` (`mode: "forward"`, `cutoff: "2026-10-08"`, `cut_kind: "date"`). Per the prompt contract for `stage: merits`, I did not anchor on `context.json`'s cert-stage `band` (`"federal"`).
- **Provisioned Filings (`record/documents/`):**
  - `questions-presented.txt` (both Questions Presented from the petition)
  - `petition.txt`, `brief-in-opposition.txt`, and `cert-reply.txt` (cert-stage briefing)
  - `merits-brief-petitioner.txt` (Solicitor General's opening brief on the merits)
  - `merits-brief-respondent.txt` (Prutehi Guahan's brief on the merits)
  - `merits-reply-petitioner.txt` (Solicitor General's reply brief on the merits)
  - `argument-transcript.txt` (transcript of the October 7, 2026 oral argument)
  - `record/argument-features.json` (deterministic speaker turn and word counts from the transcript)
- **Additional Retrieval (`forward` mode):** Via the CourtListener MCP server, I retrieved and read the Ninth Circuit's opinion below, *Prutehi Litekyan: Save Ritidian v. United States Department of the Air Force*, 128 F.4th 1089 (9th Cir. 2025) (`opinion_id: 10799245`), including Judge Berzon's majority opinion and Judge VanDyke's dissent.

---

## 2. StatPack Base Rates and Anchoring

### A. Merits Docket Base Rate (`metrics/statpack.md` — "The merits docket (granted cases)")
- **Grant Date and Grant Term:** The docket snapshot (`2026-10-08.json`) shows certiorari was granted on **March 9, 2026**, which falls in **OT2025** (`grant_term = 2025`).
- **Strictly-Prior Ten-Term Pool (`2015 <= T < 2025`):** In `metrics/statpack.md`, the "The merits docket (granted cases)" table publishes an `excluded (not in granted)` column and carries 8 grant Terms strictly prior to OT2025 that have parsed judgments (OT2017 through OT2024; OT2015 and OT2016 have no parsed judgments in the table). Pooling `disturbed` over `parsed` across OT2017–OT2024:
  - **OT2024:** 51 disturbed / 76 parsed (67.1%; 79 granted, 34 excluded)
  - **OT2023:** 35 disturbed / 56 parsed (62.5%; 56 granted, 13 excluded)
  - **OT2022:** 51 disturbed / 73 parsed (69.9%; 73 granted, 1 excluded)
  - **OT2021:** 46 disturbed / 65 parsed (70.8%; 65 granted, 3 excluded)
  - **OT2020:** 61 disturbed / 74 parsed (82.4%; 81 granted, 4 excluded)
  - **OT2019:** 46 disturbed / 58 parsed (79.3%; 60 granted, 2 excluded)
  - **OT2018:** 54 disturbed / 79 parsed (68.4%; 82 granted, 3 excluded)
  - **OT2017:** 34 disturbed / 56 parsed (60.7%; 57 granted, 6 excluded)
  - **Pooled Strictly-Prior Total (OT2017–OT2024):** **378 disturbed / 537 parsed = 70.39% (70.4%)**, out of 553 granted cases (97.1% parse coverage; 66 excluded pre-guard rows). This easily clears the 30-parsed-judgment floor and serves as the exact Brier skill baseline (`0.704`) for this cell.
  - Across those 537 parsed prior-Term decisions, the breakdown is 241 reversed (44.9%), 125 vacated (23.3%), 12 affirmed-in-part (2.2%), 143 affirmed (26.6%), 12 DIG (2.2%), and 4 equally divided (0.7%).

### B. Per-Justice Merits Votes Base Rates (`metrics/statpack.md` — "Per-Justice merits votes (complete lineups)")
Pooling the Terms strictly before the grant Term (`T < 2025`, i.e., **OT2020–OT2024** in the table, noting the table's caution that per curiams and unseatable lineups are excluded, and DIGs, equally divided Courts, and mixed judgments are left out of the disturb denominator):
- **Roberts:** Sat 238, With judgment 224 (94.1%), Disturb 159 of 228 (69.7%)
- **Kavanaugh:** Sat 238, With judgment 227 (95.4%), Disturb 165 of 228 (72.4%)
- **Barrett:** Sat 232, With judgment 211 (90.9%), Disturb 150 of 220 (68.2%)
- **Gorsuch:** Sat 236, With judgment 183 (77.5%), Disturb 152 of 222 (68.5%)
- **Alito:** Sat 235, With judgment 188 (80.0%), Disturb 138 of 222 (62.2%)
- **Thomas:** Sat 238, With judgment 187 (78.6%), Disturb 140 of 227 (61.7%)
- **Kagan:** Sat 238, With judgment 181 (76.1%), Disturb 152 of 223 (68.2%)
- **Sotomayor:** Sat 238, With judgment 172 (72.3%), Disturb 149 of 222 (67.1%)
- **Jackson (OT2022–OT2024):** Sat 147, With judgment 112 (76.2%), Disturb 95 of 139 (68.3%)

---

## 3. Assessment of the Merits Briefs and Oral Argument

Starting from the **70.4%** prior-Term disturbed base rate, three case-specific factors push `P(disturbed)` up to **0.90** (`judgment: "reversed"`):

### A. Quantitative Argument Asymmetry (`record/argument-features.json`)
First, I note the coverage reported in `record/argument-features.json`: `segments_parsed: 3` (Petitioner's opening by Mr. Liu, Respondent's argument by Mr. Henkin, and Petitioner's rebuttal by Mr. Liu), `justice_turns_attributed: 203`, `justice_turns_unattributed: 0`, and `non_justice_speaker_labels: ["MR. HENKIN", "MR. LIU"]` (100% attribution coverage of Justice turns).
- While Respondent's counsel had the lectern, the Justices intervened **136 times (2,958 words)**.
- While Petitioner's counsel had the lectern, the Justices intervened **67 times (2,022 words)**.
- **Eight of the nine Justices** spoke more turns and more words during Respondent's argument than during Petitioner's argument:
  - **Roberts:** 22 turns / 298 words to Respondent vs. 5 turns / 31 words to Petitioner
  - **Thomas:** 8 turns / 118 words to Respondent vs. 3 turns / 59 words to Petitioner
  - **Alito:** 15 turns / 348 words to Respondent vs. 9 turns / 270 words to Petitioner
  - **Sotomayor:** 25 turns / 607 words to Respondent vs. 9 turns / 487 words to Petitioner
  - **Kagan:** 16 turns / 452 words to Respondent vs. 4 turns / 91 words to Petitioner
  - **Gorsuch:** 14 turns / 216 words to Respondent vs. 4 turns / 42 words to Petitioner
  - **Kavanaugh:** 11 turns / 302 words to Respondent vs. 11 turns / 285 words to Petitioner
  - **Barrett:** 14 turns / 323 words to Respondent vs. 2 turns / 72 words to Petitioner
  - **Jackson:** 11 turns / 294 words to Respondent vs. 20 turns / 685 words to Petitioner (the sole Justice who questioned Petitioner more heavily).

While turn and word counts are mechanical measures of engagement rather than direct vote counts, higher questioning volume directed at an advocate—particularly when 8 of 9 Justices skew in the same direction—is a strong empirical indicator of judicial skepticism toward that side.

### B. Qualitative Reading of the Oral Argument on Question Presented 1
A close reading of `argument-transcript.txt` confirms that the quantitative asymmetry reflects deep, cross-ideological skepticism of Respondent's APA finality theory:

1. **Respondent's Retreat from the Permit Application and Rebuke from the Bench:**
   In its merits brief and at oral argument, Respondent attempted to distance itself from the proposition that a permit-renewal application is itself a "final agency action," arguing instead that the Air Force made an underlying substantive "decision" to conduct OB/OD operations for another three years and that the 2021 application was merely the evidence or culmination of that decision.
   - **Justice Sotomayor** squarely rejected this maneuver during Petitioner's argument, observing that the Question Presented asks whether the federal government's submission of a permit-renewal application to a state or territorial regulator is final agency action, which settles the framing for the Court's review.
   - **Chief Justice Roberts** similarly challenged Respondent's counsel on why he was retreating from the permit application named in the Question Presented, noting that counsel appeared dubious about whether a renewal application can qualify as final agency action.
   - **Justice Gorsuch** pointed out that Respondent's own complaint repeatedly tied the challenged action to the 2021 renewal application and that any challenge to an earlier operational decision or the 2018 permit was unpleaded or waived.

2. ***Bennett v. Spear* Prong 1 (Consummation of Decisionmaking):**
   - **Justice Kagan** articulated the core flaw in the Ninth Circuit's reasoning: in a permitting process, an application is the *beginning* of the process, not its *consummation*, and the fact that RCRA's cooperative-federalism structure involves two agencies (the Air Force as applicant and Guam EPA as regulator) does not turn the hand-off of an application into the consummation of the permitting process.
   - **Justice Thomas** and **Chief Justice Roberts** both emphasized that the Air Force cannot conduct OB/OD operations under the 2021–2024 permit unless and until Guam EPA grants the application.

3. ***Bennett v. Spear* Prong 2 (Legal Consequences and the Automatic Extension):**
   Respondent's fallback argument was that under Guam's RCRA regulations (22 Guam Admin. R. & Regs. § 30109(o), mirroring 40 C.F.R. § 270.51), filing a timely renewal application automatically keeps the 2018 permit in effect pending Guam EPA's disposition, thereby producing immediate legal consequences.
   - **Justice Sotomayor**, **Justice Alito**, and **Justice Barrett** all pushed back strongly against this theory. Justice Sotomayor noted that the Air Force's ongoing legal authority to operate flows from the 2018 permit (which Respondent never challenged), not from the 2021 application. Justice Alito noted that a permit application does not fit any category in the APA's definition of "agency action" (5 U.S.C. § 551(13)) and that the automatic extension operates by force of Guam law, not by any legal determination in the Air Force's application. Justice Barrett noted that the automatic extension is purely interim and disappears the moment Guam EPA acts on the application.

4. **Question Presented 2 (NEPA Displacement by RCRA) Likely Left Open:**
   While Petitioner argued under QP2 that RCRA's comprehensive permitting scheme and the 2023 Fiscal Responsibility Act amendments to NEPA (42 U.S.C. § 4336(a)(2)–(3)) displace NEPA review, **Justices Sotomayor and Kagan** questioned whether the Court needed to reach such a broad holding across all federal permit applications to state regulators. **Justice Kavanaugh** noted that several circuits already apply the functional-equivalence doctrine to RCRA and observed that reversing on QP1 avoids any need to resolve QP2. This makes a narrow, consensus reversal on QP1 overwhelmingly likely.

5. **Justice Jackson's Concern and Potential Separate Writing:**
   **Justice Jackson** was the only Justice who pressed Petitioner at length on a potential regulatory gap: because Guam EPA is a territorial agency not bound by NEPA, if the Air Force's application to Guam EPA is not final agency action, when can a plaintiff ever enforce NEPA before munitions are detonated? Mr. Liu answered that once Guam EPA issues the permit and the Air Force makes an operational decision (such as issuing an operational plan) to detonate munitions under that permit, *that* federal operational decision is final agency action reviewable under the APA. During Respondent's argument, Justice Jackson asked Respondent's counsel why suing at that post-permit stage would not suffice. I therefore predict that Justice Jackson most likely joins the judgment to reverse (writing a concurrence in the judgment to lock in the Government's representation about post-permit judicial review), while carrying a ~0.28 chance of dissenting if she concludes the automatic extension makes the renewal application immediately reviewable.

---

## 4. Calibration of Specific Fields

- **`probability` (`0.90`) and `judgment` (`"reversed"`):**
  - I allocate **0.78** to `reversed` (the standard disposition when the Court agrees with a district court's dismissal that a court of appeals reversed), **0.12** to `vacated` (in case the Court remands for the Ninth Circuit to address whether any non-application claim was preserved or frames the defect via Article III standing/ripeness), **0.09** to `affirmed`, and **0.01** to `dismissed-as-improvidently-granted` (summing to `0.90` disturbed / `0.10` undisturbed).
- **`votes`:**
  - All nine Justices are predicted in the `majority` (with Justice Jackson having `writing: "concurrence-in-judgment"` and Justice Kavanaugh `writing: "majority"`), reflecting that a 9–0 reversal in the judgment (with 1–2 separate writings) or an 8–1 reversal (Jackson dissenting) are the two dominant outcomes.
- **`claim_distributions`:**
  - **`majority-author`:** Kavanaugh (`0.180`) leads given his authorship of *Seven County Infrastructure Coalition v. Eagle County* (2025) and his D.C. Circuit administrative-law background, followed by Barrett (`0.140`), Roberts (`0.120`), Kagan (`0.120`), Alito (`0.110`), Sotomayor (`0.100`), Gorsuch (`0.090`), Thomas (`0.080`), Jackson (`0.050`), and `per-curiam` (`0.010`), summing to `1.000`.
  - **`separate-writers`:** Jackson (`0.38`) is the clear frontrunner to write separately (either concurring in the judgment on the post-permit review point or dissenting), followed by Thomas (`0.18`), Sotomayor (`0.18`), and Gorsuch (`0.16`) (who may write brief concurrences on QP2, standing, or the scope of QP1).
- **`big_case_score` (`0.55`):**
  - The case presents an important, recurring administrative and environmental law question affecting federal military and operational facilities nationwide whenever they apply for state-administered permits under cooperative-federalism statutes (RCRA, Clean Water Act, Clean Air Act). However, because the Court is poised to resolve it narrowly on APA § 704 finality without reaching the broader NEPA-displacement question (QP2), its doctrinal impact will be moderate (`0.55`).

---

## 5. Key Uncertainties

1. **`reversed` vs. `vacated`:** While `reversed` is the standard mandate when reinstating a district court dismissal, the Court occasionally enters `vacated` and remands when leaving open whether an alternative framing of the complaint was preserved below. Both count as `disturbed` on the Brier binary, so this uncertainty affects only the exact-match `judgment` label.
2. **Article III Standing vs. APA Final Agency Action:** Justices Barrett, Gorsuch, and Alito raised Article III standing/ripeness during Petitioner's argument. While the bench's questioning of Respondent overwhelmingly centered on *Bennett v. Spear* and APA § 704 finality, there is a small (~15%) chance the majority blends standing/ripeness into its threshold holding.
