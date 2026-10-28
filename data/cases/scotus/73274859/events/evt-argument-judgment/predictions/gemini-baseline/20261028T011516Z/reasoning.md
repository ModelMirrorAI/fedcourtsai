# Predictor Rationale (`reasoning.md`) — `scotus/73274859` (`evt-argument-judgment`)

## 1. Summary of Forecast

- **`probability` (`judgment-disturbed`):** `0.83` (`granted = 1`, `predicted_disposition = "other"`)
- **`judgment`:** `reversed`
- **Predicted Lineup:** 6–2 for Petitioners (Roberts, Thomas, Kagan, Gorsuch, Kavanaugh, Barrett in the majority; Sotomayor and Jackson in dissent; Alito recused).
- **`big_case_score`:** `0.92`

## 2. Provisioned Inputs Consulted

This is a `forward` mode merits cell at `moment: argued` (`context.json`: `cutoff = "2026-10-06"`, `cut_kind = "date"`, `snapshot_date = "2026-10-06"`, `snapshot_provenance = "truncated"`, `term = 2025`). I read and relied upon the following provisioned files under `data/cases/scotus/73274859/record/`:

1. **Snapshot:** `record/snapshots/2026-10-06.json` (confirming the February 23, 2026 grant order adding the statutory and Article III jurisdiction question, the September 28, 2026 Clerk's letter noting that Justice Alito will not continue to participate, and the October 5, 2026 oral argument).
2. **Filed Documents (`record/documents/`):**
   - `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, and `appendix.txt` (containing the Colorado Supreme Court's 5–2 opinion in *In re County Commissioners of Boulder County v. Suncor Energy USA, Inc.*, 2025 CO 21, by Justice Gabriel and the dissent by Justice Samour joined by Justice Boatright, as well as the Boulder County District Court's May 19, 2022 order).
   - `merits-brief-petitioner.txt`, `merits-brief-respondent.txt`, and `merits-reply-petitioner.txt`.
   - `merits-amicus-united-states.txt` — the United States filed an amicus brief supporting Petitioners and participated in oral argument through Principal Deputy Solicitor General Sarah M. Harris. The Solicitor General argued that (a) the Court has Article III and statutory jurisdiction under 28 U.S.C. § 1257(a) pursuant to both *Atlantic Richfield Co. v. Christian*, 590 U.S. 1 (2020), and the fourth category of *Cox Broadcasting Corp. v. Cohn*, 420 U.S. 469 (1975); and (b) federal law precludes Respondents' state-law claims both under the Clean Air Act and *International Paper Co. v. Ouellette*, 479 U.S. 481 (1987) (for domestic emissions) and under constitutional structure / *American Electric Power Co. v. Connecticut*, 564 U.S. 410 (2011) (*AEP*), and foreign-affairs preemption (for global emissions). My forecast closely follows the Solicitor General's position on both jurisdiction and the core *AEP*/*Ouellette*/Clean Air Act merits holding.
   - `argument-transcript.txt` (full transcript of the October 5, 2026 oral argument) and `record/argument-features.json`.

## 3. Base-Rate Anchoring (`metrics/statpack.md` and `metrics/statpack.json`)

### A. Merits Disturbed Base Rate
Certiorari was granted on February 23, 2026, placing this case in grant Term **OT2025** (`grant_term = 2025`). Following the prompt's rule for **"The merits docket (granted cases)"**, I pooled `disturbed` over `parsed` across the grant Terms strictly preceding OT2025 (`2017 <= T < 2025`, all 8 prior grant Terms present in the table; the section publishes the `excluded` guard column removing 76 pre-cohort rows):

| Grant Term | Granted | Excluded | Parsed (Coverage) | Affirmed | Reversed | Vacated | In Part | DIG | Equally Divided | Disturbed | Disturbed Rate |
| --- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| 2024 | 79 | 34 | 76 (96.2%) | 21 | 38 | 13 | 0 | 2 | 2 | 51 | 67.1% |
| 2023 | 56 | 13 | 56 (100.0%) | 17 | 22 | 13 | 0 | 4 | 0 | 35 | 62.5% |
| 2022 | 73 | 1 | 73 (100.0%) | 21 | 24 | 27 | 0 | 1 | 0 | 51 | 69.9% |
| 2021 | 65 | 3 | 65 (100.0%) | 15 | 32 | 9 | 5 | 3 | 1 | 46 | 70.8% |
| 2020 | 81 | 4 | 74 (91.4%) | 13 | 42 | 19 | 0 | 0 | 0 | 61 | 82.4% |
| 2019 | 60 | 2 | 58 (96.7%) | 11 | 33 | 11 | 2 | 1 | 0 | 46 | 79.3% |
| 2018 | 82 | 3 | 79 (96.3%) | 24 | 30 | 20 | 4 | 1 | 0 | 54 | 68.4% |
| 2017 | 57 | 6 | 56 (98.2%) | 21 | 20 | 13 | 1 | 0 | 1 | 34 | 60.7% |
| **Pooled (2017–2024)** | **553** | **66** | **537 (97.1%)** | **143** | **241** | **125** | **12** | **12** | **4** | **378** | **70.4%** |

The strictly-prior pooled merits baseline is **70.4%** (`378 / 537` parsed judgments, with `537 / 553 = 97.1%` parse coverage across those eight Terms). Within that 537-case parsed pool, plain reversals account for 44.9% (241/537), vacaturs for 23.3% (125/537), affirmed-in-part for 2.2% (12/537), plain affirmances for 26.6% (143/537), DIGs for 2.2% (12/537), and affirmances by an equally divided Court for 0.7% (4/537).

### B. Per-Justice Merits Vote Base Rates
Pooling the five Terms strictly before grant Term OT2025 (`OT2020`–`OT2024`, comprising 238 complete decisions out of 275 total documents, and 228 with a plain judgment) from **"Per-Justice merits votes (complete lineups)"** gives the following baseline rates:
- **Roberts:** sat 238, with judgment 224 (94.1%), disturb 159 of 228 (69.7%)
- **Kavanaugh:** sat 238, with judgment 227 (95.4%), disturb 165 of 228 (72.4%)
- **Barrett:** sat 232, with judgment 211 (90.9%), disturb 150 of 220 (68.2%)
- **Gorsuch:** sat 236, with judgment 183 (77.5%), disturb 152 of 222 (68.5%)
- **Thomas:** sat 238, with judgment 187 (78.6%), disturb 140 of 227 (61.7%)
- **Kagan:** sat 238, with judgment 181 (76.1%), disturb 152 of 223 (68.2%)
- **Sotomayor:** sat 238, with judgment 172 (72.3%), disturb 149 of 222 (67.1%)
- **Jackson (OT2022–OT2024):** sat 147, with judgment 112 (76.2%), disturb 95 of 139 (68.3%)
- **Alito:** sat 235, with judgment 188 (80.0%), disturb 138 of 222 (62.2%) — recused in this case.

## 4. Case-Specific Adjustments and Oral Argument Analysis

Starting from the **70.4%** strictly-prior disturbed base rate, I adjust upward to **0.83** based on three case-specific factors:

### A. Quantitative and Qualitative Oral Argument Signals
In `record/argument-features.json` (which parsed 232 attributed Justice turns and 6,961 words across 8 participating Justices, with `unattributed_turns = 0`, `unattributed_words = 0`, and `preamble_lines = 84`), the raw alignment totals show 163 turns (4,912 words) during Petitioners' and the United States' arguments versus 69 turns (2,049 words) during Respondents' argument. However, decomposing that count by speaker and advocate structure reveals why the raw aggregate is driven by two dissenting Justices and the two-advocate top-side structure:
1. Two advocates argued on the top side (Kannon Shanmugam for Petitioners: 113 turns, 3,256 words; Principal Deputy SG Sarah Harris for the United States: 50 turns, 1,656 words), each undergoing a full round of seriatim questioning, versus one advocate for Respondents (Kevin Russell: 69 turns, 2,049 words).
2. **Justices Sotomayor and Jackson alone accounted for 52.8% of all turns (86 of 163) and 56.3% of all words (2,764 of 4,912)** directed at Petitioners and the Solicitor General (Sotomayor: 38 turns / 1,196 words to Petitioner-side vs. 9 turns / 252 words to Respondent; Jackson: 48 turns / 1,568 words to Petitioner-side vs. 5 turns / 137 words to Respondent).
3. By contrast, **Chief Justice Roberts, Justice Kagan, and Justice Kavanaugh each spoke more words to Respondents' single advocate than to Petitioners' and the Solicitor General's two advocates combined**:
   - **Roberts:** 9 turns / 239 words to Respondent vs. 4 turns / 91 words to Petitioner-side.
   - **Kagan:** 13 turns / 487 words to Respondent vs. 12 turns / 285 words to Petitioner-side.
   - **Kavanaugh:** 12 turns / 428 words to Respondent vs. 9 turns / 316 words to Petitioner-side.
   - **Barrett:** 12 turns / 320 words to Respondent vs. 15 turns / 381 words across two Petitioner-side advocates (higher intensity per advocate to Respondent).

### B. Substance of the Bench's Questioning on the Merits
Six of the eight participating Justices signaled clear agreement that Boulder's state-law claims cannot proceed:
- **Justice Kagan** explicitly rejected Respondents' attempt to distinguish *AEP*, *Ouellette*, and *Milwaukee I/II*, stating that all of those cases rest on the premise that "because emissions cross state lines and go everywhere, one state can't regulate for the whole nation, let alone the whole world." She further explained that targeting upstream fossil-fuel sales rather than emissions cuts *against* Respondents because the Clean Air Act regulates emissions directly and chose not to impose liability on upstream sales.
- **Chief Justice Roberts** underscored that climate change is a "50-state problem" where emissions from around the globe mix indiscriminately, distinguishing traditional localized nuisances.
- **Justice Kavanaugh** emphasized Justice Ginsburg's statement for a unanimous Court in *AEP* that borrowing the law of a particular state is inappropriate for greenhouse-gas claims, and pointed out that under *Ouellette* allowing tort suits under affected-state law across 50 states would undermine the federal regulatory design.
- **Justice Gorsuch** pressed Respondents on why *Ouellette* alone does not require dismissal given that Boulder pleaded its claims solely under *Colorado* law (the law of the affected state) rather than the law of any source state.
- **Justice Barrett** and **Justice Thomas** focused on Clean Air Act preemption informed by *Ouellette* and *AEP* as a clean statutory basis for reversal that avoids any tension with *National Pork Producers Council v. Ross* or *Hencely*.

### C. Threshold Jurisdictional Risk and Uncertainties
The primary source of downward pressure—and the reason `probability` is **0.83** rather than >0.90—is the threshold jurisdictional question under 28 U.S.C. § 1257(a) combined with an 8-Justice bench:
- **Justices Jackson and Sotomayor** were strongly skeptical that the Colorado Supreme Court's C.A.R. 21 decision qualifies as a separate original proceeding under *Atlantic Richfield* or satisfies the fourth exception in *Cox*.
- **Justice Gorsuch** tested both sides rigorously on whether C.A.R. 21 is an exercise of appellate supervisory control under Article VI, Section 2 of the Colorado Constitution rather than an original writ under Section 3, and whether *Cox* should be expanded.
- Nevertheless, **Chief Justice Roberts** (author of *Atlantic Richfield*) defended applying *Atlantic Richfield* to defer to the Colorado Supreme Court's characterization of C.A.R. 21 as an exercise of its original jurisdiction, and **Justice Kavanaugh** and **Justice Kagan** explored why *Cox* Category 4 is satisfied (particularly after Respondents' counsel confirmed to Justice Kagan that Respondents have no standalone statutory or common-law fraud count independent of their emissions-mediated tort claims). Even if one conservative Justice (e.g., Gorsuch or Thomas) had reservations about one of the two jurisdictional pathways, at least five and likely six Justices will find jurisdiction satisfied under either *Atlantic Richfield* or *Cox* Category 4.
- Because `reversed` (~0.71) is far more likely than `vacated` (~0.11, which would occur only if the Court vacates for the Colorado courts to determine whether any narrow source-state claim was preserved), I select `"reversed"` as the modal `judgment`.

## 5. Authorship and Separate-Writing Calibration

From `metrics/statpack.json` across `OT2020`–`OT2024` (238 complete decisions), each active Justice authored ~9–12% of majority opinions (~2.5% per curiam), while separate-writing rates (`separate / sat`) were: Thomas 26.9% (64/238), Jackson 25.9% (38/147), Gorsuch 24.2% (57/236), Sotomayor 20.2% (48/238), Kavanaugh 14.3% (34/238), Barrett 9.9% (23/232), Kagan 8.0% (19/238), and Roberts 2.9% (7/238).
- For `majority-author`, I set `Alito: 0.0` (recused) and concentrate probability on the likely majority coalition, led by **Roberts (0.220)** (who assigns the opinion, authored *Atlantic Richfield*, and often retains marquee October-sitting federalism/environmental cases) and **Kavanaugh (0.210)** (who articulated the unifying *AEP*/*Ouellette*/CAA framework at argument), followed by **Barrett (0.165)**, **Gorsuch (0.135)**, **Kagan (0.115)**, and **Thomas (0.085)**.
- For `separate-writers`, I set `Alito: 0.0` and elevate **Jackson (0.55)** and **Sotomayor (0.52)** as the expected dissenters on jurisdiction and the merits, while giving **Thomas (0.38)**, **Gorsuch (0.34)**, **Kagan (0.22)**, and **Barrett (0.18)** above-baseline probabilities of concurring separately given the distinct doctrinal paths (constitutional structure vs. statutory Clean Air Act preemption, and *Atlantic Richfield* vs. *Cox* finality).
