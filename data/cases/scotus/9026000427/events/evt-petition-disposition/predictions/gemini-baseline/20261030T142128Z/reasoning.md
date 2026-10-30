# Predictor Rationale (`reasoning.md`)

## Summary of Forecast

- **Predicted disposition:** `denied` (`granted`: `0`, `probability`: `0.003`)
- **Declared claims:**
  - `disposition`: `0.003`
  - `relist-increment`: `0.02`
  - `cvsg-increment`: `0.001`
  - `summary-disposition-route`: `0.25`
  - `dissent-from-denial`: `0.005`
- **Big-case score:** `0.05`

## Base-Rate Anchor

From `record/context.json`, this cell runs in `forward` mode at `moment: distribution` for an OT2026 paid petition (`term: 2026`) with frozen conditioning `band: "baseline"` (`salience_version: "sal-v4"`), `distribution_count: 1`, `cvsg_date: null`, and `signals_observable: true`.

1. **Salience-band anchor (`sal-v4`):** Pooling the `baseline` band's bracketed `reached` grant rates in `metrics/statpack.md` across all nine Terms strictly preceding OT2026 (OT2017–OT2025) yields roughly **5.11%** (`~659.4` weighted grants over `n = 12,913` weighted resolved petitions that reached the `baseline` band: OT2025 4.0% on n=1314; OT2024 5.9% on n=1274; OT2023 5.9% on n=1312; OT2022 5.9% on n=1196; OT2021 5.7% on n=1500; OT2020 4.5% on n=1740; OT2019 4.7% on n=1399; OT2018 4.8% on n=1529; OT2017 4.9% on n=1649). By comparison, the leading (terminal) `baseline` band grant rate across those same nine Terms is **1.26%** (`n = 9,774`), and the overall modern discretionary-cert grant-family rate is **2.86%** (`692` granted + `590` GVR over `44,777` resolved cases).
2. **Originating-court cut (`cafc`):** In the modern cert slice (denial-reweighted), petitions from the Federal Circuit (`cafc`, `n = 900` resolved) have a base rate of 92.4% denied, 3.0% granted, 3.0% dismissed, and 1.6% GVR (4.6% grant family).
3. **Relist, CVSG, and amicus cuts (paid scored segment):**
   - `relist_bucket = 0` (`n = 10,203` resolved): 96.8% denied, 1.3% granted, 1.3% dismissed, 0.5% GVR (1.8% grant family).
   - `cvsg = none` (`n = 13,556` resolved): 92.4% denied, 4.1% granted, 2.3% GVR, 1.2% dismissed.
   - `cert_amicus = 0` (`n = 11,109` resolved): 95.0% denied, 2.0% granted, 1.8% GVR, 1.2% dismissed.

## Case-Specific Adjustments

Starting from the ~5.1% `baseline` band `reached` rate (and ~1.8% zero-relist rate), several strong downward factors in the provisioned snapshot (`2026-10-30.json`) and `record/documents/petition.txt` drive `P(grant)` down to **0.003 (0.3%)**:

1. **Pro se petitioner + government waiver of response:** Although filed on the paid docket (`26-427`), Petitioner Richard W. Coleman, Jr. proceeds *pro se*. On October 23, 2026, the Solicitor General (representing Respondent MSPB) waived the right to respond, and the petition was distributed on October 28, 2026 for the November 13, 2026 Conference without a call for response or any amicus support. Petitions distributed on a waiver without a call for response are almost uniformly denied at first conference.
2. **Nonprecedential per curiam decision below and absence of a circuit split:** The Federal Circuit's June 10, 2026 decision (App. 1–8) is an 8-page nonprecedential per curiam affirmance by Judges Lourie, Schall, and Taranto. The petition does not allege any circuit split. Instead, it challenges the Federal Circuit's routine application of *Bosley v. Merit Systems Protection Board*, 162 F.3d 665 (Fed. Cir. 1998), and *Yunus v. Department of Veterans Affairs*, 242 F.3d 1367 (Fed. Cir. 2001): because the Pentagon Force Protection Agency notified Petitioner on January 23, 2015 that his 25% hazardous duty pay (HDP) supplement was being discontinued effective January 24, 2015, and Petitioner's first alleged protected disclosure occurred on February 2, 2015, his disclosures postdated the discrete pay decision and could not have been a "contributing factor" under 5 U.S.C. § 2302(b)(8). Likewise, under *Bosley* and *National Railroad Passenger Corp. v. Morgan*, 536 U.S. 101 (2002), subsequent paychecks reflecting the lower pay rate are continuing effects of a prior discrete act rather than new retaliatory personnel actions.
3. **Vehicle and preservation flaws:** Even if the Court were interested in the line between continuing effects of a discrete pay termination and an independent post-disclosure "failure to take" a personnel action under 5 U.S.C. §§ 2302(a)(2)(A)(ix) and (b)(8), this case is a poor vehicle. As the Federal Circuit noted (App. 4–5), the Administrative Judge also found in the alternative that Petitioner failed to nonfrivolously allege that he made any protected disclosure under § 2302(b)(8), and the specific disclosures Petitioner tied to the April 24, 2015 position-description update (disclosures 6, 8, 10, and 11) all postdated April 24, 2015 as well. Moreover, Questions Presented 1 and 3 are heavily fact-bound, focusing on a duplicated electronic signature on an OF-8 classification form (`PD M759A`), 18 U.S.C. § 1001(a)(3), and disputed CBRN/explosives duties.

## Rationale for Secondary Claims and Distributions

- **`relist-increment` (0.02):** Across the paid scored segment in `metrics/statpack.md`, roughly 25.6% (`3,517 / 13,720`) of resolved petitions end with `1+` relists, but that pool is heavily weighted toward represented petitioners, petitions with briefs in opposition or amicus support, and cases where the Court calls for a response. For a pro se petition from a nonprecedential MSPB jurisdictional dismissal where the SG waived response, the probability of a call for response, conference relist, or administrative reschedule is roughly 2%.
- **`cvsg-increment` (0.001):** The Solicitor General is already counsel of record for Respondent MSPB. A CVSG is an invitation to the Solicitor General as amicus curiae when the United States is not a party; here, if the Court wants the government's views, it calls for a response from Respondent rather than issuing a CVSG.
- **`summary-disposition-route` (0.25):** Conditional on the remote event of a grant, GVRs account for roughly 35% of the Federal Circuit grant family in the statpack (`1.6%` GVR vs. `3.0%` plenary grant over `n = 900`). Because there is no pending Supreme Court case on which this petition would be held for a GVR, plenary review would be the primary mode if granted, leaving a 0.25 conditional probability for a summary remand/GVR (e.g., if the SG conceded a record or timing error in a called-for response).
- **`dissent-from-denial` (0.005) and `order-writers`:** Separate writings respecting denial are rare in routine pro se Federal Circuit employment cases, with slightly higher (0.001) individual probabilities assigned to Justices who more frequently author separate cert-stage statements (Thomas, Alito, Sotomayor, Gorsuch, Jackson) and lower probabilities (0.0002–0.0005) to the remaining Justices.
- **`big_case_score` (0.05):** The dispute concerns an individual federal employee's 2015 hazardous-duty-pay supplement and MSPB IRA jurisdictional pleading rules, with minimal broader doctrinal or public-policy salience.

## Uncertainties

The primary uncertainty is whether a law clerk or Justice might view the petition's assertion that early February 2015 disclosures preceded the April 24, 2015 position-description revision (`PD M759A`) as warranting a call for a response from the government (`relist-increment`). However, the Federal Circuit's opinion explains (App. 5) that before the MSPB, Petitioner tied his April 24, 2015 reassignment claim specifically to disclosures 6, 8, 10, and 11—each of which postdated April 24, 2015—making even a call for response highly improbable.
