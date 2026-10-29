# Predictor Rationale: *Allison Nguyen v. Louisiana* (No. 26-19)

## 1. Summary of Numbers

- **`granted`:** `0` (`predicted_disposition`: `"denied"`)
- **`probability` (`disposition`):** `0.045` (4.5%)
- **`relist-increment`:** `0.97` (97.0%)
- **`cvsg-increment`:** `0.002` (0.2%)
- **`summary-disposition-route`:** `0.08` (8.0% conditional on grant)
- **`dissent-from-denial`:** `0.06` (6.0% conditional on denial)
- **`big_case_score`:** `0.55`

## 2. Base-Rate Anchor

From `record/context.json`, this cell is in `mode: "forward"`, `term: 2026`, `salience_version: "sal-v4"`, `band: "baseline"`, with `distribution_count: 1`, `cvsg_date: null`, `amicus_briefs: null`, and `snapshot_date: "2026-10-29"`.

Following the anchoring protocol in `.github/prompts/predict.md`, I anchor on the `sal-v4` **bracketed `reached`** grant-family rate for the `baseline` band pooled across the Terms strictly preceding Term 2026 rendered in `metrics/statpack.md` (Terms 2022–2025; 5 of 11 Terms rendered in the table):

- **OT 2022:** `0.6% (n=1,173) [reached: 5.5% (n=1,288)]`
- **OT 2023:** `1.5% (n=1,203) [reached: 7.4% (n=1,341)]`
- **OT 2024:** `0.2% (n=1,277) [reached: 5.2% (n=1,375)]`
- **OT 2025:** `1.0% (n=1,111) [reached: 4.5% (n=1,197)]`

Pooling those four prior Terms gives a `baseline` `reached` base rate of **5.68%** (`n = 5,201`; in `metrics/statpack.json`, the corresponding `prefix_est_grant_rate` values across 2022–2025 pool to `5.42%` over `n = 5,096`). For broader context in `metrics/statpack.md`:
- Across all modern discretionary cert petitions (`n = 51,667` estimated petitions from `4,948` rows), the grant-family rate is **2.8%** (`2.1%` granted, `0.7%` GVR, `95.3%` denied, `1.8%` dismissed).
- For state-court petitions overall (`n = 11,454` from `1,039` rows), the grant-family rate is **1.6%** (`1.3%` granted, `0.3%` GVR); within the paid scored segment, petitions from the Supreme Court of Louisiana (`n = 152`) have a **5.3%** grant-family rate (`2.6%` granted, `2.6%` GVR).
- In the paid scored segment by amicus-brief count, petitions with `0` amicus briefs (`n = 6,625`, alongside an `(unknown)` coverage gap of `n = 7,619`) have a **2.3%** grant-family rate (`1.3%` granted, `1.0%` GVR).

## 3. Case-Specific Adjustments from the Anchor

Starting from the `sal-v4` `baseline` `reached` anchor of **~5.7%**, I adjust to **4.5% (`0.045`)** based on the competing signals in the provisioned snapshot (`2026-10-29.json`) and filings (`petition.txt`, `appendix.txt`):

1. **Positive signal — Call for a Response (`Oct 09 2026`):**
   - Although `context.json` places the petition in `band: "baseline"` with `distribution_count: 1`, `snapshots/2026-10-29.json` shows that after the State of Louisiana failed to respond by the initial August 5, 2026 deadline and the petition was distributed on September 15, 2026 for the October 9, 2026 Long Conference, the Court entered `Response Requested. (Due November 9, 2026)` on October 9, 2026.
   - That means the petition survived the mass Long Conference cull of un-responded petitions and attracted interest from at least one Chambers. Furthermore, the constitutional issue—whether a misdemeanor domestic abuse battery conviction carrying lifetime federal disarmament under 18 U.S.C. § 922(g)(9), a 10-year Louisiana firearm prohibition under La. R.S. 14:95.10, and permanent non-expungeability under La. C.Cr.P. art. 977(C)(2) is a "serious" offense requiring a jury trial under *Blanton v. City of North Las Vegas*, 489 U.S. 538 (1989)—was cleanly raised by pretrial motion (`App. 89a–90a`), supervisory writ (`App. 43a–46a`), direct supervisory appeal (`App. 37a–41a`), and writ application to the Louisiana Supreme Court (`App. 1a–2a`).

2. **Negative signal — The alleged conflict with *Andersen* breaks down on inspection:**
   - The petition's core claim of a split rests on the Nevada Supreme Court's decision in *Andersen v. Eighth Judicial District Court*, 135 Nev. 321, 448 P.3d 1120 (2019), which held that Nevada's misdemeanor domestic battery statute triggered a Sixth Amendment jury-trial right.
   - As the Louisiana Fifth Circuit Court of Appeal explained in both its interlocutory writ denial (`App. 45a–46a`) and its post-conviction opinion (`App. 40a–41a`), *Andersen* does not conflict with the decision below on either federal or state grounds:
     - First, under *Blanton*, 489 U.S. at 541–43, courts look to whether additional statutory penalties reflect a *legislative determination by the enacting legislature* that the offense is serious. Consequently, federal collateral consequences imposed by Congress—such as 18 U.S.C. § 922(g)(9)—do not transform a state misdemeanor into a "serious" offense. Indeed, the Nevada Supreme Court itself held in *Amezcua v. Eighth Judicial District Court*, 135 Nev. 33, 453 P.3d 1260 (2019), *cert. denied*, 141 S. Ct. 1052 (2021), that federal immigration consequences do not count under *Blanton*, and the Eleventh Circuit in *United States v. Chavez*, 204 F.3d 1305, 1313–14 (11th Cir. 2000), held that even in a federal misdemeanor prosecution, § 922(g)(9) does not trigger a jury trial right because 18 U.S.C. § 921(a)(33)(B)(i)(II) expressly contemplates predicate domestic violence misdemeanors for which the defendant was *not* entitled to a jury trial.
     - Second, on state-imposed firearm restrictions, *Andersen* turned on a Nevada statute imposing a **permanent, lifetime state-law ban** on firearm possession for misdemeanor domestic battery. By contrast, Louisiana's statute, La. R.S. 14:95.10(E), imposes only a **temporary 10-year prohibition** following completion of sentence or probation (and provides a separate felony jury trial if a defendant is ever charged with violating La. R.S. 14:95.10). Other appellate courts, such as the D.C. Court of Appeals in *Medhin v. United States*, 308 A.3d 1217, 1223–24 (D.C. 2024), have likewise distinguished *Andersen* where the jurisdiction's firearm prohibition is temporary rather than permanent.
     - Third, no state high court or federal court of appeals has held that ineligibility for expungement renders a six-month misdemeanor "serious" under *Blanton*.

3. **Negative signal — Thin petition, no amicus support, and forthcoming BIO:**
   - The petition (`petition.txt`) is brief (~10 pages of text), filed by local counsel with no amicus support, and does not address the Louisiana Fifth Circuit's distinction between Nevada's lifetime ban in *Andersen* and Louisiana's 10-year restriction in La. R.S. 14:95.10(E), nor does it address 18 U.S.C. § 921(a)(33)(B)(i)(II). Once the State files its Brief in Opposition on or around November 9, 2026 laying out those distinctions, the likelihood that four Justices vote to grant plenary review is low (`0.045`).

## 4. Rationale for Secondary Claims and Distributions

- **`relist-increment` (`0.97`):**
  - `relist-increment` resolves to `1` iff the resolution-time `distribution_count` exceeds the frozen `Prediction.context.distribution_count` (`1`).
  - While the unconditional relist rate in `Cert petitions by relist count (paid scored segment)` is `2,902 / 14,357 = 20.2%` (`11,455` ending at 0 relists vs. `1,737` at 1 relist, `516` at 2, `368` at 3–4, and `281` at 5+), this docket already records `Oct 09 2026: Response Requested. (Due November 9, 2026)` after its first distribution (`Sep 15 2026`).
  - Under Supreme Court practice, a once-distributed petition on which the Court requests a response is redistributed for a new conference after the Brief in Opposition is filed (or its time expires). Only a pre-distribution dismissal or withdrawal under Rule 46 (~2–3% probability) would prevent `distribution_count` from rising to at least `2`. Hence `P(relist-increment) = 0.97`.
- **`cvsg-increment` (`0.002`):**
  - In `Cert petitions by CVSG status (paid scored segment)`, only `128` of `15,176` petitions (`0.84%`) receive a CVSG, and CVSGs are virtually non-existent in state criminal prosecutions challenging a conviction under the Sixth Amendment.
- **`summary-disposition-route` (`0.08`):**
  - Conditional on a grant, there is no pending Supreme Court case for which *Nguyen* is a GVR hold, and the lower court's faithfulness to *Blanton* precludes a summary reversal on the merits. Thus, if granted, the case would almost certainly be set for full briefing and oral argument (`92%`), leaving an `8%` conditional probability of summary disposition.
- **`dissent-from-denial` (`0.06`) and `order-writers`:**
  - Because the Court issued a Call for Response in a low-profile state misdemeanor case sitting at the intersection of the Sixth Amendment right to a jury trial and Second Amendment disarmament, there is a meaningful (`6.0%`) conditional probability that a Justice notes a dissent or statement respecting denial.
  - In `order-writers`, probabilities are concentrated on Justice Thomas (`0.028`) and Justice Gorsuch (`0.018`), who have most frequently authored separate writings on Second Amendment and Sixth Amendment jury-trial cert denials, followed by Justice Alito (`0.008`), Justice Sotomayor (`0.004`), Justice Jackson (`0.003`), Justice Kavanaugh (`0.002`), and Chief Justice Roberts, Justice Kagan, and Justice Barrett (`0.001` each).

## 5. Main Uncertainties

- **Chambers motivation for the Call for Response:** We cannot observe which Justice requested the response on October 9, 2026 or whether that Chambers intends to push for a grant or circulate a dissent from denial once the State's opposition is filed.
- **State's Brief in Opposition:** The BIO is not yet filed (due November 9, 2026); if the State were to concede a broader conflict or raise a novel threshold issue, the dynamics at the post-BIO conference could shift slightly.
