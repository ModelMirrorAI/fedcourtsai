# Prediction Reasoning: *City of North Las Vegas, Nevada, et al. v. Genoa Jones, et al.* (`scotus/73500257`)

**Event:** `evt-order-call-for-response-disposition` (`moment: response-requested`, `stage: cert`)  
**Predictor:** `gemini-baseline` (`gemini-4-argon`)  
**Run ID:** `20261029T160941Z`  
**Input Snapshot:** `2026-07-21.json` (`cutoff: 2026-07-22`, `mode: forward`)

---

## 1. Base-Rate Anchor (`sal-v4` `baseline` Risk-Set Pool & Statpack Cuts)

Per `record/context.json`, this cell is in `mode: forward` with `term: 2025`, `distribution_count: 1`, `cvsg_date: null`, `band: baseline`, and `salience_version: sal-v4`. Under the timing and leakage rules in `.github/prompts/predict.md` and `metrics/statpack.md`, we anchor on the **bracketed `reached` (risk-set)** grant rate for the `baseline` band under `sal-v4` pooled across all shown Terms strictly prior to `OT2025` (`OT2017`–`OT2024`):

| Term | `baseline` Risk-Set Resolved (`n`) | `baseline` Risk-Set Granted | Bracketed `reached` Rate |
| :--- | ---: | ---: | ---: |
| OT2017 | 1,452 | 76 | 5.2% |
| OT2018 | 1,430 | 72 | 5.0% |
| OT2019 | 1,354 | 54 | 4.0% |
| OT2020 | 1,341 | 68 | 5.1% |
| OT2021 | 1,329 | 56 | 4.2% |
| OT2022 | 1,158 | 53 | 4.6% |
| OT2023 | 1,246 | 62 | 5.0% |
| OT2024 | 1,210 | 64 | 5.3% |
| **Pooled (`OT2017`–`OT2024`)** | **10,520** | **505** | **4.80%** |

Additional context from the committed `metrics/statpack.md` cuts (paid scored segment):
- **By Originating Circuit (`ca9`):** Across `n = 2,671` petitions from the Ninth Circuit, the grant-family rate is `4.3%` (`4.2%` `granted`, `0.1%` `gvr`), slightly below the overall modern paid-segment rate.
- **By Amicus-Brief Count (`1` amicus brief):** The snapshot shows one amicus brief docketed before the call for response (filed July 6, 2026 by the City of Henderson, Las Vegas Metropolitan Police Department, Clark County School District, Nevada Sheriffs' and Chiefs' Association, City of Sparks, City of Las Vegas, Washoe County Sheriff's Office, and International Municipal Lawyers Association). In the statpack's amicus-brief cut (`n = 1,180` for bucket `1`, alongside a large `(unknown)` bucket of `n = 11,467`), the grant-family rate is `9.2%` (`8.9%` `granted`, `0.3%` `gvr`).
- **By Relist Count / CVSG Status:** In the terminal relist-count cut, `0` relists (`n = 10,000`) has a `1.0%` grant-family rate, whereas `1` relist (`n = 1,870`) rises to `18.3%` (`17.7%` `granted`, `0.6%` `gvr`) and `2` relists (`n = 550`) rises to `21.6%`. Because this petition sits at `moment: response-requested` with `distribution_count: 1` after an initial waiver of response, it is virtually guaranteed (`0.99`) to be distributed at least once more once the Brief in Opposition arrives, placing it into the multi-distribution trajectory.

---

## 2. Case-Specific Evidence in the Provisioned Record

We read `2026-07-21.json`, `documents.json`, `questions-presented.txt`, `petition.txt`, and `appendix.txt` (all provisioned with full text, `empty_text: false`). Note that CourtListener MCP `search` queries returned HTTP 429 (daily rate limit 1400/day exceeded), so we degraded gracefully to `fedcourts query`, local `extract_citations`, and the complete provisioned record.

### A. Factual and Procedural Posture
1. **Waiver Followed by Call for Response:** Petition was docketed June 5, 2026; Respondents Genoa Jones and Cornell Tinsley filed a waiver on June 10, 2026; the petition was distributed on June 24, 2026 for the July 9, 2026 conference; municipal/law-enforcement amici filed in support of Petitioners on July 6, 2026; and on July 21, 2026, the Court called for a response (due August 20, 2026).
2. **Ninth Circuit Panel Opinion & Rehearing En Banc Dissent:** Below, a Ninth Circuit panel (Judge Mendoza, joined by Judge Friedland and District Judge Lasnik) reversed the District of Nevada's grant of qualified immunity to North Las Vegas Police Lieutenant Scott Salkoff and Officer Michael Rose on Plaintiffs' Fourth Amendment warrantless curtilage-entry claim (*Jones v. City of North Las Vegas*, 150 F.4th 1030 (9th Cir. 2025), *amended*, March 6, 2026, App. 1a–17a). Eight active Ninth Circuit judges—Judge Collins, joined by Judges Callahan, Bennett, R. Nelson, Lee, Bress, Bumatay, and Tung—dissented from the denial of rehearing en banc (App. 18a–36a).

### B. Upside Factors Driving `probability` from `0.048` up to `0.25`
1. **Strong Summary-Reversal / Error-Correction Signal:** Judge Collins's eight-judge dissent is written specifically to invite summary reversal on Prong 2 of qualified immunity under *Rivas-Villegas v. Cortesluna*, 595 U.S. 1 (2021) (per curiam), *City of Tahlequah v. Bond*, 595 U.S. 9 (2021) (per curiam), and *Stanton v. Sims*, 571 U.S. 3 (2013) (per curiam).
2. **Reliance on a Single Distinguishable Circuit Case (*United States v. Johnson*):** The panel held that a single 2001 criminal suppression decision, *United States v. Johnson*, 256 F.3d 895 (9th Cir. 2001) (en banc), put it "beyond debate" in February 2019 that hot pursuit was broken when officers lost visual contact with a fleeing domestic-battery suspect for at least 18 minutes before a K-9 unit alerted to Plaintiffs' walled backyard inside a police perimeter. Yet in *Johnson*, a misdemeanor suspect fled into rural, multi-acre wooded brush where he was uncontained, the officer abandoned the chase to look for a dropped pepper-spray canister, and 30 minutes later entered a neighbor's property on a "gut feeling" without probable cause.
3. **Panel's Editorial Modification of *Johnson* and Citation of the Passage Rebuked in *Stanton v. Sims*:** In its original opinion (App. 45a), the panel quoted *Johnson* as holding there is no hot pursuit where "'the continuity of the chase was terminated permanently.'" After the rehearing petition pointed out that here the trail was allegedly *recovered* by a K-9 alert inside an active perimeter, the panel amended its opinion to replace "permanently" with "`[has been] terminated' definitively" (App. 9a, 31a–32a). Additionally, in footnote 2 (App. 11a n.2), the panel quoted *Johnson*'s statement that a misdemeanor offense "weighs heavily against" exigent circumstances—the exact portion of *Johnson* that the Supreme Court unanimously rebuked in *Stanton v. Sims*, 571 U.S. at 9–10, as having been read "far too broadly."

### C. Downside / Vehicle Factors Keeping `denied` at `0.75`
1. **Severe Summary-Judgment Factual Disputes on Search Duration and Scope:** As the panel emphasized in footnote 1 (App. 5a n.1), on summary judgment the evidence must be viewed in the light most favorable to Plaintiffs. While Lieutenant Salkoff arrived at the perimeter 18 minutes after the suspect jumped the back wall, Salkoff admitted in his deposition that he could not remember when or where he started his search and may have searched "more than a dozen yards" (including jumping over the wall into the neighbor's yard at 3804 Vidalia without a warrant or K-9 alert, App. 56a) before entering Plaintiffs' yard, and Officer Rose testified that the search lasted "for more than an hour and possibly for two or three hours" (App. 5a n.1). Summary reversal requires a clean, undisputed factual predicate. Once Respondents' Brief in Opposition highlights that the entry into Plaintiffs' yard occurred during a multi-hour, yard-by-yard neighborhood sweep rather than an immediate 18-minute hot pursuit, the appetite for summary reversal will drop substantially.
2. **Unresolved Probable Cause Predicate (K-9 "Apocrine / Fear Odor" Alert):** The panel expressly *assumed without deciding* that Storm's alert to "apocrine" (human fear odor) from an elevated spot down the street supplied probable cause to believe the suspect was in Plaintiffs' backyard (App. 12a). The Supreme Court will be reluctant to grant or summarily reverse when an unresolved and factually unusual probable-cause question sits directly underneath the hot-pursuit issue.
3. **Post-*Lange* Low Appetite for Plenary Cert Grants on Fact-Bound Hot Pursuit:** Because *Lange v. California*, 594 U.S. 295 (2021), already settled the Fourth Amendment framework for misdemeanor flight (totality of the circumstances), Question 1 presents a fact-bound application rather than a clean post-*Lange* circuit split.

---

## 3. Justification for Quantitative Claims and Distributions

- **`granted`: `0`, `probability`: `0.25`, `predicted_disposition`: `"denied"`** — We decompose the `0.25` grant-family probability into ~`0.18` `summary-reversal`, ~`0.01` `gvr`, and ~`0.06` plenary `granted`, leaving `0.75` on `denied`.
- **`claims`:**
  - `disposition`: `0.25` (matches top-level `probability`).
  - `relist-increment`: `0.99` (the snapshot has `distribution_count: 1` and stops on the day the Court called for a response; once the BIO is filed, the petition will be distributed again for a post-BIO conference).
  - `cvsg-increment`: `0.01` (virtually zero chance of a CVSG in a local police § 1983 Fourth Amendment suit).
  - `summary-disposition-route`: `0.76` (`0.19 / 0.25 = 0.76`; conditional on a grant, summary reversal or GVR in the cert order is three times as likely as setting the case for full merits briefing and oral argument).
  - `dissent-from-denial`: `0.28` (conditional on denial, there is a ~28% chance that Justice Alito and/or Justice Thomas writes a dissent from the denial of certiorari echoing Judge Collins's 8-judge dissent).
- **`claim_distributions` (`order-writers`):** Independent per-Justice probabilities of authoring or co-authoring a separate writing on the cert order: `Alito` (`0.18`), `Thomas` (`0.14`), `Gorsuch` (`0.04`), `Kavanaugh` (`0.03`), `Sotomayor` (`0.03`), `Jackson` (`0.02`), `Roberts` (`0.01`), `Kagan` (`0.01`), `Barrett` (`0.01`).
- **`big_case_score`: `0.35`** — Moderate doctrinal and practical significance for municipal police departments conducting perimeter and K-9 searches and for § 1983 qualified-immunity standards, though fact-bound and lacking national constitutional or institutional stakes.
