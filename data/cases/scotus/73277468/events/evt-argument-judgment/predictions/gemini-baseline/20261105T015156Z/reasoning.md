# Rationale for Merits Prediction: *Jasmine Younge v. Fulton Judicial Circuit District Attorney's Office, Georgia* (No. 25-352)

## 1. Summary of Numbers

- **`probability` / `judgment-disturbed`**: `0.90` (`granted: 1`, `predicted_disposition: "other"`).
- **`judgment`**: `vacated` (`0.76` probability of vacatur and remand; `0.14` probability of reversal; `0.08` probability of affirmance; `0.02` probability of DIG).
- **`votes`**: `9-0` unanimous (`majority` for all nine sitting Justices).
- **`big_case_score`**: `0.35` (a practically important Federal Rules of Civil Procedure decision resolving an entrenched circuit split on summary judgment and pleading practice, though technically narrow and non-constitutional).

## 2. Inputs Consulted

1. **Snapshot and Conditioning Context**: Read `record/context.json` (`mode: "forward"`, `cutoff: "2026-11-03"`, `cut_kind: "date"`, `snapshot_date: "2026-11-03"`, `snapshot_provenance: "truncated"`, `term: 2025`, `band: "elevated"`, `salience_version: "sal-v6"`). Per the prompt instructions for `stage: merits`, the cert salience band (`elevated`) and `distribution_count` (`3`) are spent cert-stage signals and were not used to anchor the merits forecast. Read `record/snapshots/2026-11-03.json`, which records certiorari granted on March 30, 2026 (OT 2025 grant Term), merits briefing completed between June and October 2026, four amicus briefs filed (Professor Derek Muller in support of Petitioner; Michael J. Showalter in support of neither party; Washington Legal Foundation and State of West Virginia et al. in support of Respondent; no United States amicus participation), and oral argument held on November 2, 2026.
2. **Provisioned Documents (`record/documents/`)**: Read `documents.json`, `questions-presented.txt`, `petition.txt` (including the Eleventh Circuit's published opinion at Pet. App. 1a–30a and the Northern District of Georgia's order at Pet. App. 31a–56a), `brief-in-opposition.txt`, `cert-reply.txt`, `merits-brief-petitioner.txt`, `merits-brief-respondent.txt`, `merits-reply-petitioner.txt`, and `argument-transcript.txt`. No `merits-amicus-united-states.txt`, `decision-below.txt`, or `lower-court-docket.txt` was provisioned (the Eleventh Circuit opinion is in the petition appendix).
3. **Deterministic Argument Counts (`record/argument-features.json`)**: The pipeline parsed 289 transcript blocks across 3 advocate segments with zero unattributed blocks (`unattributed_blocks: 0`, `malformed_blocks: 0`). While Petitioner's counsel (Mr. Schnapper) was at the lectern across opening and rebuttal, the bench took 81 turns (2,434 words): Sotomayor (18 turns, 623 words), Kagan (10 turns, 405 words), Jackson (15 turns, 396 words), Gorsuch (14 turns, 297 words), Alito (6 turns, 292 words), Roberts (8 turns, 224 words), Kavanaugh (5 turns, 102 words), Thomas (4 turns, 79 words), Barrett (1 turn, 16 words). While Respondent's counsel (Mr. Petrany) was at the lectern, the bench took 64 turns (1,938 words): Jackson (18 turns, 725 words), Sotomayor (18 turns, 405 words), Kavanaugh (7 turns, 260 words), Kagan (5 turns, 201 words), Barrett (5 turns, 154 words), Gorsuch (9 turns, 134 words), Alito (1 turn, 56 words), Roberts (1 turn, 3 words), Thomas (0 turns, 0 words). As required by the prompt, raw turn/word counts are not votes; my assessment below rests on the substance of the questions in `argument-transcript.txt`.

## 3. Base Rate Anchoring (`metrics/statpack.md`)

- **Merits Disturbed Base Rate**: Certiorari in No. 25-352 was granted on March 30, 2026, which falls in **OT 2025** (`grant_term = 2025`). In `metrics/statpack.md` under **"The merits docket (granted cases)"** (which publishes the required `excluded (not in granted)` column), the grant Terms strictly preceding OT 2025 (`2015 <= T < 2025`, of which Terms 2017–2024 are present in the table) pool as follows:
  - **2024**: 51 disturbed / 76 parsed (79 granted, 14 excluded; 67.1%)
  - **2023**: 35 disturbed / 56 parsed (56 granted, 8 excluded; 62.5%)
  - **2022**: 51 disturbed / 73 parsed (73 granted, 1 excluded; 69.9%)
  - **2021**: 43 disturbed / 62 parsed (62 granted, 3 excluded; 69.4%)
  - **2020**: 60 disturbed / 73 parsed (80 granted, 3 excluded; 82.2%)
  - **2019**: 46 disturbed / 58 parsed (60 granted, 2 excluded; 79.3%)
  - **2018**: 54 disturbed / 78 parsed (81 granted, 3 excluded; 69.2%)
  - **2017**: 35 disturbed / 57 parsed (58 granted, 6 excluded; 61.4%)
  - **Pooled strictly-prior baseline (OT 2017–2024)**: `375` disturbed out of `533` parsed (`549` granted, `40` excluded), for a **70.4%** disturbed base rate (`375 / 533 = 0.70356`), well above the 30-parsed-judgment floor.
- **Per-Justice Merits Votes Reference (`metrics/statpack.md`)**: Pooling the complete-lineup tables for Terms strictly before OT 2025 (`OT 2020–2024`: 238 complete documents out of 275 total, 229 with a plain judgment):
  - **With-judgment rates (OT 2020–2024)**: Kavanaugh 227/238 (95.4%), Roberts 224/238 (94.1%), Barrett 207/228 (90.8%), Alito 188/235 (80.0%), Thomas 187/238 (78.6%), Gorsuch 183/236 (77.5%), Kagan 181/238 (76.1%), Jackson 112/147 (76.2%, OT 2022–2024), Sotomayor 172/238 (72.3%).
  - **Disturb rates on plain judgments (OT 2020–2024)**: Kavanaugh 166/229 (72.5%), Roberts 160/229 (69.9%), Gorsuch 153/223 (68.6%), Barrett 151/221 (68.3%), Kagan 153/224 (68.3%), Jackson 95/139 (68.3%, OT 2022–2024), Sotomayor 150/223 (67.3%), Alito 139/223 (62.3%), Thomas 140/228 (61.4%).

## 4. Case-Specific Adjustments from the 70.4% Baseline to 90.0%

Starting from the **70.4%** disturbed baseline, I adjust upward to **0.90** based on the merits briefing and the oral argument transcript:

1. **Textual and Structural Clarity of Rules 8(c), 15(a), and 16(b)(4)**:
   - The Eleventh Circuit in Footnote 8 of its opinion (Pet. App. 13a–14a) explicitly stated that it treats unpleaded affirmative defenses raised at summary judgment under a standalone "no prejudice" rule (*Hassan*), whereas late motions to amend pleadings must satisfy Rule 16(b)(4)'s "good cause" standard and Rule 15(a)(2).
   - That dichotomy creates a perverse incentive: a defendant that missed the scheduling order's deadline without diligence is *worse off* if it follows Rule 15 and moves to amend (triggering Rule 16(b)(4) good cause) than if it simply ignores the pleading rules and asserts the unpleaded defense directly in a summary judgment motion.
2. **Oral Argument Confirmation Across Ideological Lines**:
   - During Respondent's argument, six Justices (Jackson, Sotomayor, Kagan, Kavanaugh, Barrett, and Gorsuch) expressed pointed skepticism of Respondent's position.
   - **Justice Kavanaugh** (Tr. 55–57) and **Justice Kagan** (Tr. 46–48) highlighted the glaring asymmetry between plaintiffs and defendants: a plaintiff cannot raise an unpleaded legal claim at summary judgment on the existing discovery record without satisfying Rules 15 and 16(b)(4). Kavanaugh told Respondent's counsel that this asymmetry is a "red flag" and that Respondent's position looks like "an end run around Rule 15 and Rule 16."
   - **Justice Barrett** (Tr. 48–50) and **Justice Gorsuch** (Tr. 52–54) rejected Respondent's attempt to analogize its summary judgment motion to a purely legal argument under *Dupree v. Younger*, noting that the six-factor *Laurie* test for "personal staff" was litigated as a fact-bound summary judgment inquiry.
   - **Justice Jackson** (Tr. 36–38, 60–62) dismantled Respondent's reliance on Rule 61 harmless error, pointing out that Rule 61 governs appellate review of judicial error, not a party's noncompliance with Rules 8, 15, and 16 in the district court.
   - Meanwhile, Petitioner's counsel (Mr. Schnapper) defused the bench's only concern about Petitioner's position—whether a defendant must file a formal, separate paper titled "Motion to Amend"—by repeatedly agreeing that constructive amendment at summary judgment is permissible so long as the district court applies the substantive standards of Rules 15(a) and 16(b)(4) (Tr. 10, 14, 24–25, 31).
3. **Choice of `vacated` over `reversed` (`0.76` vs. `0.14`)**:
   - The Eleventh Circuit assumed without deciding that Title VII's personal-staff exclusion (42 U.S.C. § 2000e(f)) is an affirmative defense, and evaluated the DA's Office's late assertion solely under *Hassan*'s no-prejudice standard rather than Rules 15(a) and 16(b)(4).
   - At argument, Justices Alito, Gorsuch, Sotomayor, and Kagan all noted that whether § 2000e(f) is an element of the claim rather than an affirmative defense (and whether the DA's Office forfeited that argument below), as well as how the Rule 15/16 standards apply, are matters to be sorted out on remand after the Court vacates the Eleventh Circuit's *Hassan* ruling (e.g., Justice Gorsuch at Tr. 22: *"I have no problem proceeding on that assumption today, and they can clean up the mess on remand if they wish"*). Petitioner's own briefs likewise ask for vacatur and remand.
4. **Remaining Uncertainty (10% Undisturbed)**:
   - There is a small (~8%) chance the Court affirms on an alternative ground (e.g., concluding that § 2000e(f) is a statutory definition/element covered by Rule 12(h)(2) rather than an affirmative defense, or that the district court's ruling was harmless error under Rule 61), and a small (~2%) chance that the threshold question whether § 2000e(f) is an affirmative defense at all prompts a dismissal as improvidently granted (`dismissed-as-improvidently-granted`).
