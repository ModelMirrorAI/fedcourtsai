# Predictor Rationale (`reasoning.md`)

## 1. Summary of Call and Calibration

- **Target:** `evt-brief-judgment` (`stage: merits`, `moment: briefed`, `decision_target: judgment`) for *International Partners for Ethical Care, Inc. v. Ferguson*, No. 25-840 (`scotus/73280341`).
- **Headline Forecast:** `probability: 0.88` (`P(disturbed)`), `granted: 1`, `predicted_disposition: "other"`, `judgment: "reversed"`.
- **Decomposition of Judgment Probabilities:**
  - `reversed`: ~0.72
  - `vacated`: ~0.16
  - `affirmed-in-part-reversed-in-part`: <0.005
  - **Total Disturbed (`P(disturbed)`): 0.88**
  - `affirmed`: ~0.08
  - `dismissed-as-improvidently-granted` (DIG): ~0.04
  - `affirmed-by-an-equally-divided-court`: <0.005
  - **Total Undisturbed: 0.12**

## 2. Provisioned Baseline and Merits Briefs Consulted

This prediction is formed in `forward` mode from the provisioned snapshot `data/cases/scotus/73280341/record/snapshots/2026-10-22.json` (`cutoff: 2026-10-22`, `cut_kind: date`) and the full set of provisioned filings in `data/cases/scotus/73280341/record/documents/`:

- `questions-presented.txt` (1 page)
- `petition.txt` (153 pages, truncated at the 150 KB cap inside the appendix containing the Ninth Circuit's order denying rehearing en banc; the panel opinion at 147 F.4th 963 and the district court opinion are intact in the appendix, and I read the remainder of the en banc dissents at 161 F.4th 604 via the CourtListener MCP server)
- `brief-in-opposition.txt` (42 pages) and `cert-reply.txt` (19 pages)
- `merits-brief-petitioner.txt` (74 pages, filed September 8, 2026)
- `merits-amicus-united-states.txt` (42 pages, filed September 15, 2026, supporting Petitioners; the Court granted the Solicitor General leave to participate in oral argument on October 19, 2026)
- `merits-brief-respondent.txt` (62 pages, filed October 21, 2026)

All provisioned documents had `empty_text: false` and `ocr_derived: false`. No `merits-reply-petitioner.txt` or `argument-transcript.txt` is on the record yet because the cell is placed at `moment: briefed` (the day after Respondent's merits brief was filed, ahead of the scheduled December 2026 argument session).

## 3. Base-Rate Anchoring (`metrics/statpack.md`)

Per the stage rules for a merits cell, I ignore the cert-stage salience band in `context.json` (`band: "elevated"`, which scored the cert petition's grant likelihood prior to the June 29, 2026 grant) and anchor on the **"The merits docket (granted cases)"** section of `metrics/statpack.md`:

- **Grant Term Identification:** Certiorari was granted on June 29, 2026, which falls in **OT2025** (`grant_term = 2025`).
- **Strictly-Prior 10-Term Pool (`2015 <= T < 2025`):** The committed statpack publishes an `excluded (not in granted)` column and renders grant Terms `2017` through `2025`. Pooling the 8 available grant Terms strictly preceding OT2025 (`2017` through `2024`):
  - `granted`: 549 cases (`79 + 56 + 73 + 62 + 80 + 60 + 81 + 58`)
  - `excluded (not in granted)`: 40 cases (`14 + 8 + 1 + 3 + 3 + 2 + 3 + 6`)
  - `parsed`: 533 cases (`76 + 56 + 73 + 62 + 73 + 58 + 78 + 57`), representing **97.1% coverage** (`533 / 549`) and clearing the 30-parsed-judgment floor by a wide margin.
  - `disturbed`: 375 cases (`51 + 35 + 51 + 43 + 60 + 46 + 54 + 35`), broken down across the 533 parsed judgments as **238 `reversed` (44.7%)**, **125 `vacated` (23.5%)**, **12 `in part` (2.3%)**, **142 `affirmed` (26.6%)**, **12 `DIG` (2.3%)**, and **4 `equally divided` (0.8%)**.
  - **Pooled Strictly-Prior Disturbed Base Rate:** `375 / 533 = 70.36%` (**~70.4%**).

## 4. Case-Specific Adjustments from the 70.4% Anchor to 88.0%

Several strong, converging signals justify adjusting upward by ~17.6 percentage points from the 70.4% merits disturbed base rate to **0.88**:

1. **Direct Alignment with the Court's 2025–2026 Standing and Parental-Rights Precedents:**
   - In *Mirabelli v. Bonta*, 607 U.S. 492 (Mar. 2, 2026) (per curiam), six Justices (Roberts, Thomas, Alito, Gorsuch, Kavanaugh, and Barrett) vacated a Ninth Circuit stay in a California parental-exclusion gender-identity case and explicitly stated (slip op. at 6): *"First, the parents protected by the injunction very likely have standing because they are objects of the challenged exclusion policies. See Diamond Alternative Energy, LLC v. EPA, 606 U.S. 100, 114 (2025)."*
   - In *First Choice Women's Resource Centers, Inc. v. Davenport*, 608 U.S. ___ (Apr. 29, 2026), a unanimous 9–0 Court (opinion by Justice Gorsuch) reversed a Rule 12(b)(1) dismissal and held that pre-enforcement chilling of First Amendment rights and pressure to modify conduct in response to state investigatory/regulatory authority constitute present Article III injury without waiting for state-court enforcement.
   - In *Bost v. Illinois State Board of Elections*, 607 U.S. 71 (Jan. 14, 2026), a 7–2 Court reversed a Seventh Circuit Rule 12(b)(1) standing dismissal; notably, Justice Barrett's concurrence in the judgment (joined by Justice Kagan) emphasized that reasonable pocketbook or behavioral mitigation steps taken at the pleading stage to avoid a credible risk of future harm are cognizable injuries under *Monsanto Co. v. Geertson Seed Farms*, 561 U.S. 139 (2010), rather than "self-inflicted" harms under *Clapper*.
   - The Court granted certiorari here on June 29, 2026—shortly after deciding *Bost*, *Mirabelli*, and *First Choice*, and after Judges VanDyke, Bumatay, and Tung dissented from the denial of rehearing en banc below (161 F.4th 604)—specifically to address the Ninth Circuit's standing barrier in parental-rights litigation after denying review in earlier cases (*Eau Claire*, *John & Jane Parents 1*, *Foote*) where the parent plaintiffs had not alleged that their own children suffered from gender dysphoria.

2. **United States Amicus Participation Supporting Petitioners:**
   - The Solicitor General filed a merits amicus brief supporting Petitioners (`merits-amicus-united-states.txt`) and was granted divided argument on October 19, 2026. Historically, SG merits participation supporting the petitioner is one of the strongest predictors of reversal.
   - More importantly, the SG's brief solves the main doctrinal vulnerability in Petitioners' merits brief. While Petitioners' merits brief leads with a sweeping theory (relying on *Deanda v. Becerra*, 96 F.4th 750 (5th Cir. 2024)) that Washington's 2023 amendment immediately abrogates every fit parent's legal right to notice, the SG's brief (at pp. 11–26, 26–30) demonstrates why the Court need not adopt a categorical rule that would allow any parent without a gender-dysphoric child to sue. Instead, because *these* individual plaintiffs specifically allege that their minor children currently suffer from gender dysphoria, that Child 5C (age 13) *has already run away from home* over gender-identity conflicts while seeing a supportive school counselor, and that Child 2D's transgender older sister *threatened to take 2D away to a "safe place"*, the complaint easily satisfies traditional "substantial risk" standing under *Susan B. Anthony List* and present mitigation/chilling standing under *Monsanto* and *First Choice* at the Rule 12(b)(1) pleading stage.

3. **Why `reversed` (0.72) is Preferred Over `vacated` (0.16):**
   - Both Petitioners (`merits-brief-petitioner.txt` at 55) and the United States (`merits-amicus-united-states.txt` at 30) ask the Court to **reverse** the judgment of the court of appeals.
   - In *Bost*, *First Choice*, and *Diamond Alternative Energy*, when the Court reviewed a court of appeals decision affirming a Rule 12(b)(1) dismissal and held that at least one plaintiff had adequately pleaded Article III standing, the Court entered a judgment of **"Reversed and remanded"** (`reversed`), rather than vacating to ask the court of appeals to re-apply the standard. A vacatur (`vacated`, ~16%) remains a secondary possibility if the Courtmerely vacates the Ninth Circuit's *Clapper* analysis and remands for application of *First Choice* and *Mirabelli* without definitively resolving standing on the pleadings.

4. **Downside Risks (`affirmed` ~0.08, `DIG` ~0.04):**
   - Respondent (`merits-brief-respondent.txt` at 17–24) presses for a DIG because Petitioners' merits brief elevated the "direct abrogation / object of the statute" theory over the "substantial risk / chilled parenting" theories emphasized in the petition. While this creates a ~4% DIG tail risk ( roughly double the 2.3% historical base rate), a DIG is unlikely because the Question Presented expressly covers the statutory removal of notice and the SG's brief squarely argues the substantial-risk and chilled-parenting theories adjudicated below.
   - Respondent also argues (`merits-brief-respondent.txt` at 5–10, 41–54) that Wash. Rev. Code § 13.32A.082 merely lifts a state-created 72-hour reporting mandate on private licensed shelters rather than forbidding shelters from contacting parents, and points to a state declaration in separate litigation asserting that zero youth have used the gender-affirming-care notice exception since 2023. While these arguments will likely anchor a 2- or 3-Justice dissent under *Clapper* and *Murthy v. Missouri*, they are unlikely to command a majority on a Rule 12(b)(1) motion to dismiss where the complaint's well-pleaded allegations must be taken as true.

## 5. Per-Justice Votes and Authorship Distributions

In the **"Per-Justice merits votes (complete lineups)"** section of `metrics/statpack.md`, pooling the strictly-prior Terms (`OT2020`–`OT2024`, 238 complete decisions, 229 with a plain judgment; `OT2022`–`OT2024` for Justice Jackson, 147 complete decisions, 139 with a plain judgment):

- **Roberts:** 224/238 (94.1%) with judgment; 160/229 (69.9%) disturb
- **Kavanaugh:** 227/238 (95.4%) with judgment; 166/229 (72.5%) disturb
- **Barrett:** 211/232 (90.9%) with judgment; 151/221 (68.3%) disturb
- **Alito:** 188/235 (80.0%) with judgment; 139/223 (62.3%) disturb
- **Thomas:** 188/238 (79.0%) with judgment; 140/228 (61.4%) disturb
- **Gorsuch:** 183/236 (77.5%) with judgment; 153/223 (68.6%) disturb
- **Kagan:** 181/238 (76.1%) with judgment; 153/224 (68.3%) disturb
- **Sotomayor:** 172/238 (72.3%) with judgment; 150/223 (67.3%) disturb
- **Jackson (`OT2022`–`OT2024`):** 112/147 (76.2%) with judgment; 95/139 (68.3%) disturb

Conditioning on the Court's 2026 votes in *Mirabelli v. Bonta* (6–3 per curiam: Roberts, Thomas, Alito, Gorsuch, Kavanaugh, Barrett in the majority; Sotomayor, Kagan, Jackson dissenting) and *Bost v. Illinois State Board of Elections* (7–2: Roberts, Thomas, Alito, Gorsuch, Kavanaugh in the majority; Barrett and Kagan concurring in the judgment on mitigation injury; Jackson and Sotomayor dissenting under *Clapper*), I forecast a **6–3 vote lineup** (`Roberts`, `Thomas`, `Alito`, `Gorsuch`, `Kavanaugh`, `Barrett` in `majority`; `Sotomayor`, `Kagan`, `Jackson` in `dissent`), while recognizing that Justice Kagan has the highest crossover probability among the three liberal Justices if the opinion tracks the SG's narrow Rule 12(b)(1) rationale.

For `majority-author`, I weight `Roberts` (`0.190`), `Barrett` (`0.175`), `Kavanaugh` (`0.160`), `Gorsuch` (`0.145`), and `Alito` (`0.135`) highest based on their authorship of *Bost*, *Murthy*, *Diamond Alternative Energy*, *First Choice*, and *Mahmoud*. For `separate-writers`, I assign elevated probabilities to `Thomas` (`0.38`) and `Alito` (`0.35`) (who have a strong incentive to concur on the broader *Mirabelli*/*Deanda* direct-abrogation theory that the SG asks the Court to avoid) and to `Jackson` (`0.36`, author of the *Bost* dissent) and `Sotomayor` (`0.34`) on the dissenting side.
