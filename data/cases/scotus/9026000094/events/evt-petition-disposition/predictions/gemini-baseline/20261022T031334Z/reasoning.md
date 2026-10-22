# Predictor Rationale (`gemini-baseline`)

## 1. Summary of Prediction

- **Predicted Disposition:** `denied` (`granted = 0`)
- **`probability` / `disposition`:** `0.12`
- **`relist-increment`:** `0.25`
- **`cvsg-increment`:** `0.01`
- **`summary-disposition-route`:** `0.72`
- **`dissent-from-denial`:** `0.08`
- **`big_case_score`:** `0.28`

## 2. Base-Rate Anchoring (`metrics/statpack.md`)

From `record/context.json`, this cell is in `forward` mode at `stage: cert`, `moment: distribution`, with `term: 2026`, `salience_version: "sal-v4"`, `band: "elevated"`, `distribution_count: 2`, and `cvsg_date: null`.

Per the prompt contract, I anchor on the **"Segment base rate by salience band (sal-v4)"** table in `metrics/statpack.md`, pooling the **bracketed `reached`** rate for the `elevated` band across all rendered Terms strictly preceding OT2026 (OT2017–OT2025):

- **OT2025:** 13.5% ($n = 312$, ~42.12 grants)
- **OT2024:** 17.9% ($n = 336$, ~60.14 grants)
- **OT2023:** 17.5% ($n = 354$, ~61.95 grants)
- **OT2022:** 19.0% ($n = 300$, ~57.00 grants)
- **OT2021:** 20.5% ($n = 342$, ~70.11 grants)
- **OT2020:** 16.1% ($n = 397$, ~63.92 grants)
- **OT2019:** 13.8% ($n = 334$, ~46.09 grants)
- **OT2018:** 15.9% ($n = 347$, ~55.17 grants)
- **OT2017:** 17.5% ($n = 400$, ~70.00 grants)

Pooling across OT2017–OT2025 yields **526.50 / 3,122 = 16.86%** (~16.9%).

Supporting signal cuts in `metrics/statpack.md` (paid scored segment):
- **Relist count = 1 (`distribution_count = 2`):** 85.7% denied, 8.3% granted, 5.1% GVR, 1.0% dismissed (total grant family = **13.4%** over $n = 2,521$ resolved).
- **CVSG = none:** 92.7% denied, 3.9% granted, 2.3% GVR (total grant family = **6.2%** over $n = 13,494$).
- **Originating circuit (`ca9`):** 94.9% denied, 2.1% granted, 1.1% GVR in the overall modern cert slice (3.2% grant family).

## 3. Case-Specific Adjustments from the Provisioned Record

 I read the provisioned snapshot (`2026-10-22.json`) and all three provisioned filings in `record/documents/` (`questions-presented.txt`, `petition.txt`, and `brief-in-opposition.txt`, none of which were truncated or `empty_text`).

### Factors Supporting Review (Upward Pressure)
1. **Call for a Response (CFR) and Subsequent Relist:** After Respondent initially waived a response on August 17, 2026, and the petition was distributed for the October 16, 2026 conference, the Court requested a response on October 6, 2026 (before the conference met). Respondent filed the BIO on October 15, Petitioners replied on October 20, and the petition was distributed a second time on October 21 for the November 6, 2026 conference.
2. **Experienced Supreme Court Counsel and Judge Collins's Dissent:** Petitioners are represented by Gibson, Dunn & Crutcher LLP, and Judge Daniel Collins authored a sharp dissent below arguing that the panel majority contradicted Respondent's own framing of the factual basis for his no-contest plea.
3. **Recent Summary Reversals on Party Presentation:** The Court recently issued summary reversals enforcing the party-presentation principle in *Clark v. Sweeney*, 607 U.S. 7 (2025) (per curiam), and *United States v. Margolin*, 146 S. Ct. 1288 (2026) (per curiam).

### Factors Weighing Against Review (Net Downward Adjustment from 16.9% to 12.0%)
1. **Why `distribution_count` Is 2:** In this docket, the first distribution (September 30 for the October 16 conference) occurred on a waiver before the Court called for a response on October 6. Thus, the second distribution (October 21 for the November 6 conference) is the *first* distribution with the BIO and Reply on the table, rather than a classic post-briefing conference relist where the Justices have already considered the fully briefed case and held it over to draft an opinion or summary order. Petitions whose second distribution is simply the post-CFR distribution convert to grants at a meaningfully lower rate than true post-BIO relists.
2. **Fact-Bound Record Dispute in an Unpublished Disposition:** The BIO (`brief-in-opposition.txt`, pp. 11–16) effectively dismantles the party-presentation claim. Unlike *Clark* and *Margolin*, where appellate courts vacated judgments on theories neither party had raised, the exact question the Ninth Circuit majority decided—whether the plea record indivisibly established that all four phases of Cardenas's conduct formed the factual predicate for his single misdemeanor § 148(a)(1) count under *Lemos* and *Sanders*—was the central issue briefed by both parties and flagged for supplemental briefing by the district court (`Pet. App. 18a ¶ 27`). Respondent's statement in the background section of his brief that he analyzed the incident "based on the four corners of Brice's eight page police report which formed the factual bases for his criminal plea" was immediately followed by his argument that Phases 1–3 each independently satisfied § 148(a)(1) without relying on Phase 4 (the stairwell tasing). Whether the state plea form's "may consider" box and unspecified reference to "the police report" satisfied *Heck* is a quintessential fact-bound dispute in an unpublished memorandum disposition.
3. **No Live Split on Fed. R. Evid. 410(a) and Poor GVR Case:** Petitioners candidly concede (`Pet. 3, 21–23`) that the Ninth Circuit panel decision cited in Footnote 1 (*King v. Villegas*, 156 F.4th 979 (9th Cir. 2025)) was vacated for rehearing en banc on April 3, 2026 (171 F.4th 1163), and that the parties in *King* abandoned the Rule 410(a) ground at the en banc stage (which was argued on June 2, 2026 and remains pending). Furthermore, because Footnote 1 in *Cardenas* expressly introduced *King* as an "[a]lternative[]" point (`Pet. App. 3a n.1`), the panel's judgment rests independently on its primary holding in the main text that the plea record did not tie the § 148(a)(1) conviction to the stairwell tasing. Under *Lawrence v. Chater*, 516 U.S. 163, 167 (1996), a GVR is unwarranted when the intervening vacatur affects only an alternative footnote and would not change the outcome below.
4. **Recent *Heck* Precedent:** As Respondent notes, the Court's recent unanimous decision in *Olivier v. City of Brandon*, 607 U.S. 552 (2026), cautioned against over-reading *Heck*'s "necessarily imply" language beyond its proper bounds, and the Court has repeatedly denied certiorari in Ninth Circuit *Heck* cases (*Smith v. City of Hemet*, *Roberts v. City of Fairbanks*, *Lemos v. County of Sonoma*).

Weighing the 16.86% `elevated` band reached base rate (and 13.4% relist-1 base rate) against the fact that the second distribution here reflects a post-waiver CFR rather than a post-BIO conference relist, plus the unpublished, fact-bound nature of the primary holding and the alternative nature of Footnote 1, I set `probability = 0.12` (roughly 7% summary reversal / GVR and 5% plenary grant).

## 4. Secondary Claims and Big Case Score

- **`relist-increment` (0.25):** Because the November 6, 2026 conference is the first conference after the BIO and Reply were filed, there is a 25% chance the Court relists the petition at least once more (e.g., if a Justice takes a closer look at Judge Collins's dissent or considers whether to hold for *King v. Villegas* en banc), and a 75% chance it denies certiorari outright on the first conference with full briefing.
- **`cvsg-increment` (0.01):** Near zero; municipal policing / state-plea-record dispute with no federal interest.
- **`summary-disposition-route` (0.72):** Conditional on a grant, summary disposition (either a per curiam summary reversal on party-presentation/*Heck* grounds or a GVR in light of the vacatur of *King v. Villegas*) is far more likely than setting an unpublished misdemeanor plea-form dispute for full merits briefing and oral argument. In the statpack's `relist_bucket = 1` row, GVRs alone are 38% of grants (5.1% / 13.4%), and here Petitioners explicitly seek summary reversal or GVR as primary/alternative remedies.
- **`dissent-from-denial` (0.08):** Judge Collins's dissent and the ongoing friction over Ninth Circuit *Heck* doctrine create a modest (~8%) chance that a Justice notes a dissent or statement respecting the denial of certiorari.
- **`big_case_score` (0.28):** Below average stakes if decided; the primary issue turns on how to read a California county plea form in an unpublished disposition, and the broader Rule 410(a) question is already mooted by the Ninth Circuit's en banc vacatur of *King*.
