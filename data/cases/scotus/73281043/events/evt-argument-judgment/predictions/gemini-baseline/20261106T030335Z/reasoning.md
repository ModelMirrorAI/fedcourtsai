# Predictor Rationale — *Guerrero v. Johnson* (No. 25-1003, `evt-argument-judgment`)

## Summary of Call

- **Stage / Moment:** `merits` / `argued` (`evt-argument-judgment`)
- **Mode:** `forward` (`context.json` cutoff `2026-11-05`, snapshot `2026-11-05.json`)
- **Predicted Judgment:** `reversed`
- **P(judgment below is disturbed):** `0.89` (`granted: 1`, `predicted_disposition: "other"`)
- **Predicted Vote Lineup:** 7–2 to reverse (Roberts, Thomas, Alito, Kagan, Gorsuch, Kavanaugh, Barrett in the majority; Sotomayor and Jackson in dissent).

## Base-Rate Anchor (`metrics/statpack.md`)

Per the prompt contract for a merits-stage cell, the salience band (`high` in `context.json`) and cert-stage signals (`distribution_count: 3`) are spent cert-stage observations and are not used as anchors.

Instead, I anchor on the committed **"The merits docket (granted cases)"** table in `metrics/statpack.md`, which publishes an `excluded (not in granted)` column and therefore passes the pool-guard check. The grant date on the docket is **June 15, 2026**, which falls in **OT2025** (`grant_term = 2025`). Pooling `disturbed` over `parsed` across the ten grant Terms strictly preceding OT2025 (`2015 <= T < 2025`, where the table holds 8 Terms from OT2017 through OT2024):

| Grant Term | Granted | Excluded (not in granted) | Parsed | Disturbed | Disturbed Rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2024 | 79 | 1 | 77 | 52 | 67.5% |
| 2023 | 56 | 0 | 56 | 35 | 62.5% |
| 2022 | 73 | 1 | 73 | 51 | 69.9% |
| 2021 | 62 | 3 | 62 | 43 | 69.4% |
| 2020 | 80 | 3 | 73 | 60 | 82.2% |
| 2019 | 60 | 2 | 58 | 46 | 79.3% |
| 2018 | 81 | 3 | 78 | 54 | 69.2% |
| 2017 | 58 | 6 | 57 | 35 | 61.4% |
| **Total (OT2017–OT2024)** | **549** | **19** | **534** | **376** | **70.4% (376 / 534)** |

The pooled sample of **534 parsed judgments** (out of **549 granted** cases, 97.3% parse coverage, with 19 excluded cert-order dispositions outside `granted`) comfortably clears the 30-judgment floor and yields a baseline disturbed rate of **70.4%** (`0.704`).

For the per-Justice vote block, I also consult the **"Per-Justice merits votes (complete lineups)"** section in `metrics/statpack.md`, pooling the decision Terms strictly before `grant_term = 2025` (OT2020–OT2024, covering 238 complete lineups of 275 documents, 230 with a plain judgment):
- **Roberts:** with judgment 224/238 (94.1%), disturb 161/230 (70.0%)
- **Kavanaugh:** with judgment 227/238 (95.4%), disturb 167/230 (72.6%)
- **Barrett:** with judgment 211/232 (90.9%), disturb 152/222 (68.5%)
- **Gorsuch:** with judgment 183/236 (77.5%), disturb 153/224 (68.3%)
- **Thomas:** with judgment 189/238 (79.4%), disturb 140/229 (61.1%)
- **Alito:** with judgment 188/235 (80.0%), disturb 139/224 (62.1%)
- **Kagan:** with judgment 181/238 (76.1%), disturb 154/225 (68.4%)
- **Sotomayor:** with judgment 172/238 (72.3%), disturb 151/224 (67.4%)
- **Jackson (OT2022–OT2024):** with judgment 112/147 (76.2%), disturb 96/140 (68.6%)

## Provisioned Filings Consulted

All provisioned documents in `data/cases/scotus/73281043/record/documents/` were read (none had `empty_text: true`, and only `petition.txt` had a minor appendix truncation of 8,208 characters at the very end of the 117-page PDF):
1. `questions-presented.txt` and `petition.txt` (filed Feb. 19, 2026) — Petitioner Eric Guerrero's cert petition and appendix (including the Fifth Circuit's unpublished panel decision answering the certified § 1292(b) question, the district court's 2022 order denying dismissal, the 2019 Fifth Circuit authorization order in *In re Johnson*, 935 F.3d 284, and Judge Ho's dissent from denial of rehearing en banc at 164 F.4th 398).
2. `brief-in-opposition.txt` (filed Apr. 24, 2026) and `cert-reply.txt` (filed May 8, 2026).
3. `merits-brief-petitioner.txt` (filed July 30, 2026) and `merits-reply-petitioner.txt` (filed Oct. 19, 2026).
4. `merits-amicus-united-states.txt` (filed Aug. 6, 2026) — The United States filed as amicus curiae **supporting Petitioner**, urging reversal on the ground that both 28 U.S.C. § 2244(b)(2)(A) and the parallel federal-prisoner provision in 28 U.S.C. § 2255(h)(2) turn on whether the Supreme Court had announced the retroactive constitutional rule before the initial petition concluded, not on whether the prisoner had a viable factual or legal basis to prevail at the time.
5. `merits-brief-respondent.txt` (filed Sept. 18, 2026).
6. `argument-transcript.txt` (argued Nov. 4, 2026) and `argument-features.json`.

## Adjustments from the 70.4% Baseline to 0.89

I adjust upward significantly from the 70.4% prior-Term merits disturbed base rate to **0.89** (`reversed`) based on four convergent factors:

### 1. Statutory Text, Grammar, and Structure Strongly Favor Petitioner
Section 2244(b)(2)(A) permits a second or successive state habeas claim only if "the applicant shows that the claim relies on a new rule of constitutional law, made retroactive to cases on collateral review by the Supreme Court, that was previously unavailable."
- Grammatically, "that was previously unavailable" modifies "a new rule of constitutional law, made retroactive to cases on collateral review by the Supreme Court." That reading is confirmed beyond doubt by 28 U.S.C. § 2255(h)(2), enacted at the same time in AEDPA, which requires a successive federal motion to contain "a new rule of constitutional law, made retroactive to cases on collateral review by the Supreme Court, that was previously unavailable"—where "claim" does not appear in the sentence at all.
- *Atkins v. Virginia*, 536 U.S. 304 (2002), was decided in 2002, five years before Johnson's 2007 trial and nine years before his 2011 initial federal habeas petition. Thus, *Atkins* was neither a "new rule" as to Johnson (since it preceded the finality of his conviction under *Teague v. Lane*) nor "previously unavailable" during his first federal habeas proceeding.
- What changed between 2011 and 2019 were (a) the May 2013 publication of the DSM-5 (moving away from a strict IQ 70 cutoff), (b) this Court's decisions in *Hall v. Florida* (2014) and *Moore v. Texas* (2017 & 2019) rejecting Texas's *Briseno* factors, and (c) new 2019 neuropsychological testing yielding an IQ score of 70. None of those is "a new rule of constitutional law, made retroactive to cases on collateral review by the Supreme Court." Indeed, every circuit to consider the question (including the Fifth Circuit) holds that *Moore* is not retroactive on collateral review. The Fifth Circuit's *In re Cathey* rule—equating changes in diagnostic standards with the availability of an *Atkins* claim whenever the claim previously lacked "some possibility of merit"—creates an extra-textual futility exception that end-runs both § 2244(b)(2)(A)'s Supreme Court retroactivity requirement (*Tyler v. Cain*) and § 2244(b)(2)(B)'s restriction of newly discovered evidence to actual innocence of the underlying offense.

### 2. United States Amicus Participation Supporting Petitioner
The Solicitor General filed a merits amicus brief supporting Petitioner and participated in oral argument (handled by Vivek Suri). Because § 2255(h)(2) uses virtually identical language for federal prisoners, the federal government has a direct institutional stake in foreclosing the Fifth and Ninth Circuits' "some possibility of merit" standard. Historically, the Court disturbs the judgment below at an elevated rate when a State petitioner is joined by the Solicitor General as amicus curiae against a Fifth Circuit habeas grant/authorization.

### 3. Oral Argument Dynamics (`argument-transcript.txt` and `argument-features.json`)
While a question from the bench is not a vote, the oral argument transcript and its deterministic turn/word counts provide strong confirmation that a clear majority—spanning both the conservative bloc and Justice Kagan—rejects Respondent's statutory reading:
- **Deterministic Turn/Word Counts (`argument-features.json`):** The parser achieved complete attribution coverage (`unattributed_turns: 0`, `unattributed_words: 0`, `header_anomalies: []`, across 3 segments: `petitioner` William Peterson with 50 turns / 1,936 words; `united-states-supporting-petitioner` Vivek Suri with 23 turns / 898 words; and `respondent` Jeremy Schepers with 33 turns / 918 words, totaling 73 petitioner-aligned turns / 2,834 words vs. 33 respondent turns / 918 words).Note that Petitioner and the United States shared the top of the hour across two separate argument segments (including full seriatim rounds), which accounts for their larger aggregate turn count, whereas several conservatives (Thomas, Kavanaugh, Barrett) asked zero questions of Respondent's counsel during his segment.
- **Qualitative Content of the Questioning:**
  - **Justice Kagan** (9 turns / 489 words to Petitioner; 3 turns / 206 words to US; 6 turns / 316 words to Respondent) was openly skeptical of Respondent's statutory argument. When questioning Respondent's counsel, she stated directly that she struggled to see how the statutory text could mean what Respondent wanted it to mean: *Atkins* was available in 2002, and what was unavailable to Respondent earlier was either the factual predicate (new IQ testing and the DSM-5) or *Moore* (which is not retroactive). She observed that § 2244(b)(2)(A) addresses legal developments while § 2244(b)(2)(B) addresses factual developments, and that Respondent was trying to shoehorn a factual or non-retroactive development into (b)(2)(A).
  - **Justice Gorsuch** (15 turns / 546 words to Petitioner; 6 turns / 281 words to Respondent) pressed Petitioner only on why Texas even needed its secondary "new rule" argument when the "previously unavailable" text ("that" modifying "rule") already decided the case, and then pressed Respondent on why an unpreserved *Ford*/*Panetti* ripeness theory had anything to do with the Question Presented under § 2244(b)(2)(A).
  - **Justice Kavanaugh** (4 turns / 338 words to Petitioner; 3 turns / 160 words to US; 0 turns to Respondent) emphasized that even where a prisoner has a sympathetic substantive claim, federal habeas review is tightly constrained by AEDPA's text, pointing to executive clemency as the traditional safety valve when AEDPA forecloses successive federal litigation.
  - **Justice Alito** (5 turns / 145 words to Petitioner; 3 turns / 106 words to US; 5 turns / 172 words to Respondent) challenged Respondent on how publication of a third-party manual by the American Psychiatric Association (the DSM-5) could possibly transform an old rule into a "previously unavailable" rule of constitutional law, and asked the United States to confirm that under *Teague*, a rule is "new" only if announced after the defendant's conviction became final.
  - **Justice Barrett** (2 turns / 55 words to Petitioner; 1 turn / 105 words to US; 0 turns to Respondent) focused on ensuring that reversing on "previously unavailable" would not inadvertently disrupt cases where a rule was announced before the initial petition but made retroactive by the Supreme Court only afterward (*Tyler v. Cain*).
  - **Chief Justice Roberts** (14 turns / 159 words total, mostly presiding plus substantive exchanges with the US) questioned whether "new rule" is evaluated relative to the initial conviction or relative to the initial petition.
  - **Justices Sotomayor and Jackson** were the only Justices who actively defended a pathway for Respondent. Justice Jackson (9 turns / 462 words to Petitioner; 7 turns / 270 words to US; 5 turns / 192 words to Respondent) and Justice Sotomayor (8 turns / 569 words to Petitioner; 4 turns / 225 words to US; 9 turns / 206 words to Respondent) pressed Petitioner and the United States on the substantive nature of *Atkins* (analogizing to *Ford v. Wainwright* and *Panetti v. Quarterman* where an eighth-amendment bar on execution cannot be adjudicated until the condition ripens or state law permits it) and even suggested to Respondent's counsel that he might have conceded too much by treating *Atkins* as a static 2002 rule rather than an evolving substantive prohibition.

### 4. Judgment Label (`reversed` vs. `vacated`)
The Fifth Circuit entered a definitive answer ("Yes") to the single certified legal question under 28 U.S.C. § 1292(b)—whether § 2244(b)(2)(A) permits Johnson's successive petition under the Fifth Circuit's "some possibility of merit" standard—and affirmed the district court's denial of the Director's motion to dismiss. Both Petitioner (Merits Br. 46) and the United States (US Amicus Br. 29) ask the Court to **reverse** the judgment of the court of appeals. Because reversing the Fifth Circuit's answer to the certified question resolves the statutory issue and requires dismissal of the successive petition under § 2244(b)(2) & (4), `reversed` is the appropriate judgment call over `vacated`.

## Uncertainties and Discount Factors

A reader should note two modest sources of uncertainty that keep `probability` at `0.89` rather than `0.95+`:
1. **Interlocutory Posture (§ 1292(b)):** Although no Justice suggested dismissing the writ as improvidently granted during oral argument, the case arrives on interlocutory review of a certified question (`Whether there can be judicially created exceptions to 28 U.S.C. § 2244(b)(2)(A)`) that the Fifth Circuit panel re-framed around its *Cathey* precedent. There is a small residual tail risk (~2–3%) of a procedural disposition or DIG, and a modest chance (~8%) that a majority affirms on a narrow theory tied to Texas's unconstitutional *Briseno* regime.
2. **Exact Dissent Count (7–2 vs. 6–3 vs. 8–1/9–0):** Justice Kagan's questioning at oral argument strongly signaled that she agrees with Petitioner's reading of the statutory text, making 7–2 the modal lineup. However, it is possible that Justice Kagan joins a narrow concurrence in the judgment, or conversely that Justices Sotomayor and/or Jackson join a narrow textual opinion that explicitly leaves open *Panetti* or original-habeas avenues.
