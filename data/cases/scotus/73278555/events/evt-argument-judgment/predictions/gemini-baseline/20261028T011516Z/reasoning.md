# Predictor Rationale (`reasoning.md`): *Anderson v. Intel Corporation Investment Policy Committee*, No. 25-498 (`scotus/73278555`)

## I. Summary of Numbers

- **Stage / Moment / Mode**: `merits` / `argued` (`evt-argument-judgment`) / `forward` (cutoff and snapshot date `2026-10-07`).
- **Predicted Judgment**: `affirmed` (`predicted_disposition: "other"`).
- **Binary Forecast (`granted` / `probability`)**: `granted: 0`, `probability: 0.18` (an 18% probability that the Ninth Circuit's judgment is disturbed via reversal, vacatur, or affirmance in part, and an **82% probability that the judgment is left undisturbed**, overwhelmingly via plain affirmance).
- **Declared Claim (`judgment-disturbed`)**: `0.18`.
- **Predicted Lineup**: 9–0 `majority` for all nine Justices.

---

## II. Provisioned Inputs Consulted

All forecasts in this cell were formed exclusively from the provisioned case record in `data/cases/scotus/73278555/record/` and the committed `metrics/statpack.md`:
1. **Snapshot**: `2026-10-07.json` (truncated at `2026-10-07`, showing the January 16, 2026 grant of certiorari in OT2025, merits briefing, the United States' amicus brief supporting Respondents and leave to participate in oral argument, and the October 6, 2026 oral argument). Per the merits-stage instructions, `record/context.json`'s cert-stage `band` (`elevated`) and `distribution_count` (`2`) are spent cert-stage signals and were not used to anchor the merits forecast.
2. **Cert-Stage and Lower-Court Documents**: `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, and `appendix.txt` (containing Judge Miller's opinion for the Ninth Circuit, 137 F.4th 1015, Judge Berzon's concurring opinion, and the Northern District of California's dismissal orders).
3. **Merits Briefs**: `merits-brief-petitioner.txt`, `merits-brief-respondent.txt`, `merits-reply-petitioner.txt`, and `merits-amicus-united-states.txt`. The **United States filed as amicus curiae supporting Respondents**, urging the Court to affirm the Ninth Circuit's judgment and hold that ERISA duty-of-prudence claims predicated on underperformance require a meaningful benchmark sharing similar aims and risks; our forecast follows the Solicitor General's recommendation closely.
4. **Oral Argument Transcript and Deterministic Features**: `argument-transcript.txt` and `argument-features.json`.

---

## III. Statpack Base-Rate Anchoring (`metrics/statpack.md`)

### 1. Merits Disturbed Rate (`grant_term - 10 <= T < grant_term`)
Certiorari in No. 25-498 was granted on **January 16, 2026**, placing the case in **grant Term OT2025** (`grant_term = 2025`). Under the merits anchoring rule in `.github/prompts/predict.md`, we pool `disturbed` over `parsed` across the grant Terms strictly preceding 2025 (`2015 <= T < 2025`). In `metrics/statpack.md` (*The merits docket (granted cases)*), eight strictly prior Terms are present (**OT2017–OT2024**, with OT2015–OT2016 omitted for having zero parsed judgments):
- **Pooled `granted` (OT2017–OT2024)**: `553` granted cases (`57 + 82 + 60 + 81 + 65 + 73 + 56 + 79`).
- **Pooled `excluded (not in granted)` (OT2017–OT2024)**: `66` cases removed by the pool guard (`6 + 3 + 2 + 4 + 3 + 1 + 13 + 34`).
- **Pooled `parsed` coverage (OT2017–OT2024)**: `537` parsed, dated judgments out of `553` granted (`97.1%` parse/completion coverage; well above the 30-case minimum floor).
- **Pooled breakdown (OT2017–OT2024, `n=537`)**: `143` affirmed (`26.6%`), `241` reversed (`44.9%`), `125` vacated (`23.3%`), `12` affirmed in part (`2.2%`), `12` DIG (`2.2%`), `4` equally divided (`0.7%`).
- **Pooled strictly-prior disturbed rate**: **`378 / 537 = 70.4%`** (`70.39%`).

### 2. Per-Justice Merits Votes Reference (`metrics/statpack.md`)
In `metrics/statpack.md` (*Per-Justice merits votes (complete lineups)*), the Terms strictly preceding grant Term 2025 are **OT2020–OT2024** (complete lineups out of total documents: OT2024 `53/63` complete, `51` plain judgment; OT2023 `48/54` complete, `46` plain; OT2022 `46/50` complete, `44` plain; OT2021 `51/60` complete, `48` plain; OT2020 `40/48` complete, `39` plain). Pooling strictly prior Terms OT2020–OT2024 (and OT2022–OT2024 for Justice Jackson):
- **Roberts**: With judgment `224 / 238` (`94.1%`); Disturb `159 / 228` (`69.7%`).
- **Kavanaugh**: With judgment `227 / 238` (`95.4%`); Disturb `165 / 228` (`72.4%`).
- **Barrett**: With judgment `211 / 232` (`90.9%`); Disturb `150 / 220` (`68.2%`).
- **Alito**: With judgment `188 / 235` (`80.0%`); Disturb `138 / 222` (`62.2%`).
- **Thomas**: With judgment `187 / 238` (`78.6%`); Disturb `140 / 227` (`61.7%`).
- **Gorsuch**: With judgment `183 / 236` (`77.5%`); Disturb `152 / 222` (`68.5%`).
- **Jackson** (OT2022–OT2024): With judgment `112 / 147` (`76.2%`); Disturb `95 / 139` (`68.3%`).
- **Kagan**: With judgment `181 / 238` (`76.1%`); Disturb `152 / 223` (`68.2%`).
- **Sotomayor**: With judgment `172 / 238` (`72.3%`); Disturb `149 / 222` (`67.1%`).

---

## IV. Case-Specific Adjustments from the 70.4% Disturbed Baseline to 18.0%

Moving from the `70.4%` strictly-prior disturbed baseline down to `0.18` (`82%` undisturbed / `affirmed`) is a large adjustment, driven by three converging factors:

### 1. Vehicle Selection and the Solicitor General's Support for Respondents
The circuit split pitted the Eighth, Seventh, Tenth, Eleventh, and Ninth Circuits (requiring a meaningful benchmark for underperformance claims) against the Sixth Circuit in *Johnson v. Parker-Hannifin Corp.*, 122 F.4th 205 (6th Cir. 2024) (rejecting that requirement over Judge Murphy's dissent). The Court previously called for the Solicitor General's views in *Parker-Hannifin* (No. 24-1030), where the government endorsed the meaningful-benchmark rule, and then granted *Anderson*—where the Ninth Circuit affirmed dismissal under the meaningful-benchmark standard and the Solicitor General (joined by the Department of Labor) supports Respondents on the merits. Taking a case from the majority side of a circuit split where the administering agency supports Respondents strongly signals that the Court granted certiorari to affirm and bring the outlier circuit (*Parker-Hannifin*) into line.

### 2. Quantitative Oral Argument Disparity (`argument-features.json`)
In `record/argument-features.json` (coverage: `132` total Justice turns, `131` attributed across `4` of `4` attributed segments, `1` turn outside segments [the Chief Justice's opening invocation], `0` unattributed-segment or unresolved turns, `closing_line: true`):
- **Petitioner alignment total**: **84 turns, 1,994 words** (`83` turns / `1,987` words during Mr. Wessler's opening argument; `1` turn / `7` words during rebuttal).
- **Respondent alignment total**: **47 turns, 1,311 words** (`38` turns / `1,041` words during Mr. McCloud's argument for Respondents; `9` turns / `270` words during Ms. Brown's argument for the United States supporting Respondents).
- **Per-Justice alignment counts (Petitioner turns/words vs. Respondent-side turns/words)**:
  - **Jackson**: `22` turns (`478` words) to Petitioner vs. `4` turns (`166` words) to Respondent side.
  - **Gorsuch**: `18` turns (`364` words) to Petitioner vs. `8` turns (`119` words) to Respondent side.
  - **Kavanaugh**: `18` turns (`360` words) to Petitioner vs. `0` turns (`0` words) to Respondent side.
  - **Sotomayor**: `8` turns (`154` words) to Petitioner vs. `4` turns (`78` words) to Respondent side.
  - **Alito**: `6` turns (`225` words) to Petitioner vs. `4` turns (`83` words) to Respondent side.
  - **Thomas**: `4` turns (`80` words) to Petitioner vs. `4` turns (`47` words) to Respondent side.
  - **Roberts**: `5` turns (`68` words) to Petitioner vs. `9` turns (`182` words) to Respondent side.
  - **Barrett**: `2` turns (`84` words) to Petitioner vs. `8` turns (`231` words) to Respondent side.
  - **Kagan**: `1` turn (`181` words) to Petitioner vs. `6` turns (`405` words) to Respondent side.

Petitioners' counsel absorbed **64.1% of attributed Justice turns (`84 / 131`) and 60.3% of Justice words (`1,994 / 3,305`)**. Even more tellingly, the turns directed by Chief Justice Roberts, Justice Barrett, and Justice Kagan to Respondents and the Solicitor General were not hostile challenges to the judgment below, but collaborative opinion-drafting inquiries about how broadly to articulate the meaningful-benchmark standard while affirming.

### 3. Qualitative Bench Consensus Across All Nine Justices
While a question from the bench is not a formal vote, the substance of the questioning here left almost no doubt about the bench's lean:
- **Thomas** immediately challenged Petitioners' premise that an equity-heavy bull-market fund can be compared to a downside-protection fund ("you can't compare apples and oranges").
- **Kagan** called Petitioners' portrayal of the Ninth Circuit's opinion a "caricature," noting that the Ninth Circuit merely required "a fund with the same general approach and risk/reward profile" rather than identical underlying assets, and later explicitly asked the Solicitor General to "flyspeck" the Ninth Circuit's reasoning "consistent with that disposition [affirmance]" so the Court could write a helpful opinion.
- **Roberts** characterized Petitioners' complaints about their specific benchmarks as "just an objection to the application of the rule in your particular case" rather than a basis to reject the rule, and emphasized that the meaningful-benchmark test "has to do some meaningful work."
- **Alito** rejected Petitioners' invocation of "holistic" pleading as "kind of a magic word" that cannot salvage apples-to-oranges comparisons, and remarked to the Solicitor General that Respondents' counsel "would be satisfied with an affirmance in any opinion. I certainly would if I were in his position."
- **Gorsuch** and **Barrett** pressed Petitioners' counsel on retreating from the Question Presented, and worked with Respondents' counsel on how to state the holding—answering the QP "yes," defining "meaningful" via statutory "like aims and strategies" ("similar, not identical"), and noting per Judge Berzon's concurrence that non-comparative claims do not require a benchmark.
- **Kavanaugh** questioned whether relative underperformance is even probative of an imprudent fiduciary process when half of all funds perform below the median in any period, and agreed with the Ninth Circuit's conclusion that using hedge funds to mitigate risk is not per se imprudent.
- **Sotomayor** and **Jackson** both defended the Ninth Circuit's reading of the complaint: Sotomayor agreed that the Ninth Circuit did not require identical asset allocations and rightly faulted the complaint for failing to identify peer funds with a long-term risk-management objective, while Jackson quoted the Ninth Circuit's opinion (Pet. App. 16a–18a) to refute Petitioners' claim that the panel ignored their non-performance asset-allocation allegations.

### 4. Residual Uncertainty (18% Disturbed Probability)
Why set `probability: 0.18` rather than `< 0.05`? In prior unanimous ERISA pleading cases (*Hughes v. Northwestern University*, 595 U.S. 170 (2022); *Fifth Third Bancorp v. Dudenhoeffer*, 573 U.S. 409 (2014)), the Court vacated and remanded after clarifying the governing pleading standard so the court of appeals could re-evaluate the complaint in the first instance. There remains a modest tail risk (~15% `vacated`, ~3% `reversed`) that if the Court refines how asset-allocation differences affect benchmark selection, it could vacate and remand rather than affirm outright. However, because Justices across the ideological spectrum explicitly agreed at oral argument that Judge Miller's opinion already applied the right standard and addressed Petitioners' non-performance allegations separately, outright affirmance (`0.82`) is substantially more likely than vacatur.

---

## V. Rationale for Authorship and Separate-Writer Distributions

In `metrics/statpack.json`, across OT2017–OT2025, majority opinion assignments among the current nine Justices are roughly balanced (~9–12% per Justice per Term), while separate-writing rates (`separate / sat`) are highest for Jackson (~32% in OT2022–OT2025), Thomas (~24%), Gorsuch (~24%), Sotomayor (~20%), Alito (~15%), Kavanaugh (~14%), Barrett (~10%), Kagan (~8%), and Roberts (~2%).
- For **`majority-author`**, we upweight **Barrett (`0.215`)** and **Kagan (`0.195`)** above the ~11% uniform baseline because both Justices actively road-tested the exact doctrinal framing of the majority opinion during Respondents' and the Solicitor General's arguments, followed by **Kavanaugh (`0.140`)**, **Gorsuch (`0.110`)**, **Roberts (`0.100`)**, and **Sotomayor (`0.090`)** (author of *Hughes* and *Cunningham v. Cornell University*).
- For **`separate-writers`**, we adjust the historical separate-writing base rates downward slightly to reflect the high unanimity and low polarization of ERISA pleading cases, while retaining meaningful probability on **Jackson (`0.20`)**, **Gorsuch (`0.18`)**, and **Kavanaugh (`0.18`)**, each of whom articulated a distinct concurring theme at argument (Jackson on non-comparative/plan-level asset-allocation theories; Kavanaugh and Gorsuch on Judge Murphy's *Parker-Hannifin* critique of underperformance claims and Judge Berzon's concurrence).
