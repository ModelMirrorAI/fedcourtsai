# Prediction Rationale: *St. Mary Catholic Parish in Littleton, Colorado, et al. v. Lisa Roy, et al.* (No. 25-581)

## 1. Summary of Numbers

- **`probability` (P(judgment below disturbed)):** `0.85` (`granted: 1`)
- **`judgment`:** `reversed` (with `predicted_disposition: "other"`)
- **`claims`:** `judgment-disturbed: 0.85`
- **`big_case_score`:** `0.88`
- **Expected Vote Lineup:** **6–3** (`Roberts`, `Thomas`, `Alito`, `Gorsuch`, `Kavanaugh`, `Barrett` in `majority`; `Sotomayor`, `Kagan`, `Jackson` in `dissent`)

---

## 2. Mode, Provisioned Record, and Baseline Anchoring

### A. Cell Mode and Provisioned Inputs
Per `record/context.json`, this cell runs in **`forward` mode** (`cutoff: "2026-11-04"`, `cut_kind: "date"`, `snapshot_date: "2026-11-04"`, `snapshot_provenance: "truncated"`, `term: 2025`). Although `record/context.json` records `band: "elevated"` (`salience_version: "sal-v6"`, `distribution_count: 3`), that salience band is a cert-stage construct that scored the petition's grant likelihood prior to the April 20, 2026 grant order; per the merits-stage contract, I do not anchor on the cert band table.

I read the provisioned snapshot `record/snapshots/2026-11-04.json` (`input_snapshot: "2026-11-04.json"`) and the provisioned documents in `record/documents/` listed in `documents.json`:
- `questions-presented.txt` (cert-stage QPs; cert was granted April 20, 2026 limited to Questions 1 and 2, declining Question 3 on overruling *Employment Division v. Smith*)
- `petition.txt`, `brief-in-opposition.txt` (marked `truncated: true`), and `cert-reply.txt`
- `merits-brief-petitioner.txt` (Petitioners' opening brief on the merits)
- `merits-amicus-united-states.txt` (brief of the United States as amicus curiae supporting Petitioners, urging **reversal**)
- `merits-brief-respondent.txt` (Respondents' brief on the merits)
- `merits-reply-petitioner.txt` (Petitioners' reply brief on the merits)
- `argument-transcript.txt` (153-page transcript of the November 3, 2026 oral argument) and `record/argument-features.json`

None of the provisioned documents had `empty_text: true` or `ocr_derived: true`, and no contact scrub placeholders (`contact_scrubbed: false`) were triggered. No `decision-below.txt` or `lower-court-docket.txt` was staged in `record/documents/`, so my reading of the Tenth Circuit's opinion (`153 F.4th 1216`) and the district court's bench-trial findings (`736 F. Supp. 3d 956`) comes from the detailed summaries and citations in the parties' and Solicitor General's briefs.

### B. Statpack Merits Baseline Anchor (`metrics/statpack.md`)
Per the merits-stage rules, the anchor is the **"The merits docket (granted cases)"** section of `metrics/statpack.md`, which publishes an `excluded (not in granted)` column and therefore passes the pool guard.
- **Grant Term Determination:** Although the petition was docketed in OT2025 (`No. 25-581`), the docket snapshot (`2026-11-04.json`) shows that certiorari was granted on **April 20, 2026**, which falls in **OT2025** (`grant_term = 2025`).
- **Strictly-Prior Merits Pool (`grant_term - 10 <= T < 2025`):** Pooling `disturbed` over `parsed` across the grant Terms strictly before `2025` rendered in `metrics/statpack.md` (Terms **2017 through 2024**, 8 Terms available in the table):
  - **OT2024:** 51 disturbed / 76 parsed (67.1%; 79 granted, 14 excluded; coverage 76/79 = 96.2%)
  - **OT2023:** 35 disturbed / 56 parsed (62.5%; 56 granted, 8 excluded; coverage 56/56 = 100.0%)
  - **OT2022:** 51 disturbed / 73 parsed (69.9%; 73 granted, 1 excluded; coverage 73/73 = 100.0%)
  - **OT2021:** 43 disturbed / 62 parsed (69.4%; 62 granted, 3 excluded; coverage 62/62 = 100.0%)
  - **OT2020:** 60 disturbed / 73 parsed (82.2%; 80 granted, 3 excluded; coverage 73/80 = 91.3%)
  - **OT2019:** 46 disturbed / 58 parsed (79.3%; 60 granted, 2 excluded; coverage 58/60 = 96.7%)
  - **OT2018:** 54 disturbed / 78 parsed (69.2%; 81 granted, 3 excluded; coverage 78/81 = 96.3%)
  - **OT2017:** 35 disturbed / 57 parsed (61.4%; 58 granted, 6 excluded; coverage 57/58 = 98.3%)
  - **Pooled Strictly-Prior Total (OT2017–OT2024):** **375 disturbed / 533 parsed = 70.36% (`0.704`)**, out of 549 granted (overall parsed-to-granted coverage **533 / 549 = 97.1%**, with 40 excluded across those eight Terms). Within those 533 parsed cases, the breakdown is **238 reversed (44.7%)**, **125 vacated (23.5%)**, **12 affirmed-in-part (2.3%)**, **142 affirmed (26.6%)**, **12 DIG (2.3%)**, and **4 equally divided (0.8%)**.
  - This 533-case pool easily clears the 30-case minimum floor (`375 / 533 = 70.4%`), providing a strong, well-populated baseline anchor of **`0.704`**.

### C. Per-Justice Merits Votes Reference (`metrics/statpack.md`)
Pooling the **"Per-Justice merits votes (complete lineups)"** table across the Terms strictly before `grant_term = 2025` (**OT2020 through OT2024**, 238 complete documents with 219 plain judgments):
- **Chief Justice Roberts:** Sat 238, With judgment **224 (94.1%)**, Disturb **160 of 225 (71.1%)**.
- **Justice Kavanaugh:** Sat 238, With judgment **227 (95.4%)**, Disturb **166 of 225 (73.8%)**.
- **Justice Barrett:** Sat 232, With judgment **211 (90.9%)**, Disturb **151 of 221 (68.3%)**.
- **Justice Alito:** Sat 235, With judgment **188 (80.0%)**, Disturb **149 of 223 (66.8%)**.
- **Justice Thomas:** Sat 238, With judgment **187 (78.6%)**, Disturb **140 of 228 (61.4%)**.
- **Justice Gorsuch:** Sat 236, With judgment **183 (77.5%)**, Disturb **153 of 223 (68.6%)**.
- **Justice Kagan:** Sat 238, With judgment **181 (76.1%)**, Disturb **155 of 224 (69.2%)**.
- **Justice Sotomayor:** Sat 238, With judgment **172 (72.3%)**, Disturb **150 of 223 (67.3%)**.
- **Justice Jackson (OT2022–OT2024):** Sat 147, With judgment **112 (76.2%)**, Disturb **95 of 139 (68.3%)**.

---

## 3. Case-Specific Adjustments from the 70.4% Baseline to `0.85`

Starting from the **70.4%** strictly-prior disturbed baseline, I adjust upward to **0.85** (`judgment: "reversed"`) based on three converging case-specific signals:

### A. United States Amicus Support (`merits-amicus-united-states.txt`)
The Solicitor General filed an amicus brief on the merits supporting Petitioners and participated in oral argument urging **outright reversal** of the Tenth Circuit's judgment on both Question 1 and Question 2. Specifically, the United States argued that:
1. Under *Fulton* and *Tandon*, Colorado's UPK equal-opportunity requirement is not generally applicable because (a) CDEC's regulatory catchall (`8 CCR 1404-1 § 4.109(A)(9)`) reserves individualized discretion to approve provider-requested programmatic preferences (and CDEC has approved 17 such preferences, including housing-assistance, dual-language, Montessori, and employer-designated preferences), and (b) CDEC allows categorical exceptions for IEP disability providers and Head Start low-income providers even though disability and income level are protected in the exact same statutory clause (`Colo. Rev. Stat. § 26.5-4-205(2)(b)`).
2. Under *Carson v. Makin* and *Sherbert v. Verner*, conditioning participation in a public tuition-benefit program on forsaking religious admissions exercises triggers strict scrutiny even when the condition is not phrased as an express exclusion of "sectarian" schools.
3. Colorado's refusal to exempt Petitioners fails strict scrutiny as a matter of law under *Fulton*.

### B. Oral Argument Transcript and Quantitative Features (`argument-transcript.txt` & `argument-features.json`)
First, checking `record/argument-features.json` (which has complete coverage: `237` total Justice turns, `236` attributed across `4` attributed segments, `1` turn outside segments, `0` unrecognized or unresolved labels, `closing_line: true`):
- Overall alignment totals show **161 turns / 6,299 words** during Petitioners' side (90 turns / 3,999 words to Petitioners' counsel Mr. Reaves; 71 turns / 2,300 words to Deputy SG Ms. Harris) versus **75 turns / 2,900 words** during Respondents' counsel Ms. Norton.
- Because a raw turn/word count does not measure *what* was asked or *why* (and here Petitioners' side had two separate advocates at the lectern), breaking the counts down by Justice alongside the transcript text is critical:
  - The three liberal Justices accounted for **81 turns / 3,926 words** of the questioning directed at Petitioners' side (**Sotomayor** 41 turns / 964 words; **Jackson** 28 turns / 1,795 words; **Kagan** 12 turns / 1,167 words), while asking Respondent's counsel Ms. Norton almost nothing (**Sotomayor** 2 turns / 5 words; **Kagan** 1 turn / 76 words; **Jackson** 8 turns / 396 words).
  - By contrast, the conservative Justices focused their substantive, skeptical questioning on Respondent's counsel Ms. Norton (**Alito** 22 turns / 647 words to Respondent vs. 6 turns / 219 words to Petitioners; **Kavanaugh** 15 turns / 721 words to Respondent vs. 15 turns / 666 words to Petitioners; **Barrett** 12 turns / 757 words to Respondent vs. 23 turns / 809 words to Petitioners; **Roberts** 14 turns / 260 words to Respondent vs. 21 turns / 255 words to Petitioners, which includes procedural speaker-recognition turns).

Second, reading the transcript (`argument-transcript.txt`) shows why at least six Justices signaled that the Tenth Circuit's judgment cannot stand:
1. **Chief Justice Roberts's critique of Colorado's *Fulton* defense:** While Chief Justice Roberts questioned Mr. Reaves about whether *Carson*'s broadest language was aimed at clever recharacterizations of express religious discrimination (Tr. 12–14), he was sharply skeptical of Respondent's counsel Ms. Norton on Question 1 (*Fulton* general applicability). He pointed out (Tr. 91–93) that Respondent Dawn Odean (Colorado's UPK Director) had testified under oath at trial that CDEC could use its regulatory catchall to approve preferences for racial minorities, gender-nonconforming students, or LGBTQ students, and that Respondents' brief (at p. 49) had been forced to disavow its own witness ("Ms. Odean was mistaken"): *"And it strikes me that you're trying to have your cake and eat it too. You clearly want to exercise discretion in a way that runs contrary to the strict non-discrimination principle when you walk through them, when your witness does, and yet, to preserve your rigorous interpretation of it that excludes any consideration of religion, you have to abandon what that person said."*
2. **Justice Gorsuch and Justice Alito on the statutory and regulatory exemptions:** Justice Gorsuch walked through the text of `8 CCR 1404-1 § 4.109` and Ms. Odean's testimony (Tr. 89–90, 99–101), emphasizing that CDEC's catchall regulation expressly lists "housing assistance" as an approved programmatic preference even though both "income level" and "lack of housing" are protected categories in `§ 26.5-4-205(2)(b)`. Justice Alito pressed Ms. Norton relentlessly (Tr. 77–80, 94–99) on how Colorado can allow providers to turn away children based on disability or income level—categories governed by the exact same statutory words ("regardless of")—while treating Petitioners' religious admissions rules as categorically barred.
3. **Justice Kavanaugh on secular pedagogical preferences vs. religious community preferences:** Justice Kavanaugh repeatedly challenged Ms. Norton (Tr. 102–113) on why Colorado approves matching preferences for Montessori, Waldorf, STEM, and Dual Language Immersion schools—allowing them to prefer families committed to their educational philosophy—while denying Catholic preschools the ability to prefer families committed to a Catholic educational community, invoking both *Fulton*/*Tandon* and *Carson v. Makin*.
4. **Justice Barrett's careful doctrinal probing:** Justice Barrett tested both sides thoroughly. With Mr. Reaves and Ms. Harris (Tr. 33–38, 64–70), she probed whether Petitioners' broadest reading of *Carson* (Question 2) would displace *Smith* across all neutral conditions in government benefit programs (such as vaccination rules or corporal-punishment bans). With Ms. Norton (Tr. 113–123), however, she pressed Respondent on whether *Mahmoud v. Taylor* and *Hurley* support Petitioners' right to maintain a cohesive religious school community and tested the mechanics of the UPK matching algorithm. Just as in *Fulton*, where Justice Barrett declined to overrule *Smith* immediately while joining the Court's general-applicability holding in full, Question 1 provides a clean, narrow doctrinal ground on which she and Chief Justice Roberts comfortably join Justices Thomas, Alito, Gorsuch, and Kavanaugh.

### C. Why `reversed` Rather Than `vacated` (and Residual Uncertainty)
- In the OT2017–OT2024 statpack merits pool, disturbed judgments split roughly 2:1 between `reversed` (238/375 = 63.5% of disturbed) and `vacated` (125/375 = 33.3% of disturbed).
- Here, `reversed` is substantially more likely than `vacated` because (1) the case went to a full bench trial and final judgment, (2) the district court already addressed strict scrutiny in the alternative on the full trial record, (3) both Petitioners and the Solicitor General ask for outright reversal, and (4) in *Fulton*, *Carson*, *Espinoza*, and *Kennedy*, the Court applied strict scrutiny itself and reversed outright.
- **Main Uncertainties (the 15% complement):** The primary way the judgment below is *not* disturbed (`0.15`) is if Chief Justice Roberts and Justice Barrett conclude (alongside Justices Sotomayor, Kagan, and Jackson) that UPK's algorithmic matching preferences do not actually authorize any provider to *refuse* an assigned child (`8 CCR 1404-1 § 4.109` vs. `§ 26.5-4-205(2)(b)`) and that *Carson* does not extend to facially neutral public-accommodations-style conditions. I view that outcome as unlikely (~14% affirmance, ~1% DIG) given Chief Justice Roberts's pointed skepticism of Colorado's witness disavowal and Justice Barrett's past alignment in *Fulton* and *Mahmoud*.
