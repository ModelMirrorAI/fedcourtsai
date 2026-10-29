### Summary of Forecast

- **Top-level `probability` (`disposition`):** `0.25` (`granted: 0`, `predicted_disposition: "denied"`)
- **`relist-increment`:** `0.99`
- **`cvsg-increment`:** `0.02`
- **`summary-disposition-route`:** `0.85`
- **`dissent-from-denial`:** `0.03`
- **`big_case_score`:** `0.42`

### Base-Rate Anchoring (`metrics/statpack.md`)

1. **Salience Band Anchor (`sal-v4`):**
   `record/context.json` freezes `band: "baseline"`, `salience_version: "sal-v4"`, `distribution_count: 1`, `cvsg_date: null`, `term: 2025`, and `mode: "forward"`. In `metrics/statpack.md` under *Segment base rate by salience band (`sal-v4`)*, the table renders two Terms strictly preceding OT 2025:
   - **OT 2023 (`2023`):** `baseline` terminal grant rate `0.0%` (`n=159`), bracketed `[reached 1.9%, n=316]`.
   - **OT 2024 (`2024`):** `baseline` terminal grant rate `0.3%` (`n=334`), bracketed `[reached 3.8%, n=578]`.
   Pooling the `reached` counts across the strictly prior Terms shown (`2023` and `2024`): `(0.019 * 316 + 0.038 * 578) / (316 + 578) ≈ (6 + 22) / 894 = 28 / 894 = 3.13%` (`~3.1%`).

2. **Other Statpack Cuts:**
   - **Modern discretionary-cert petitions by disposition:** Overall grant family is `3.9%` (`3.2%` granted + `0.7%` GVR, `n=18,743` reweighted).
   - **Originating circuit (`ca9`):** In *Cert petitions by originating circuit*, the Ninth Circuit (`ca9`, `n=3,316`) has a `3.7%` grant rate (`3.0%` granted + `0.7%` GVR) and `93.5%` denial rate.
   - **Relist count (paid scored segment):** At prediction time (`2026-07-22`), the petition had been distributed once (`relist 0` bucket terminal rate `0.1%`, `n=493`), though the Court's call for a response guarantees a post-response distribution (moving the case into the `1` or `2+` distribution buckets, where `1` relist grants at `5.2%` [`4.0%` granted + `1.1%` GVR, `n=348`] and `2` relists at `27.8%` [`25.0%` granted + `2.8%` GVR, `n=36`]).
   - **Amicus-brief count (paid scored segment):** The provisioned snapshot (`2026-07-22.json`) and live corpus row show `0` amicus briefs filed in `25-1376` (`0` bucket rate `2.7%` [`2.1%` granted + `0.6%` GVR, `n=296`], with `(unknown)` at `n=581`).

### Case-Specific Adjustments from the Provisioned Record and Forward Context

1. **The Provisioned Record (`2026-07-22.json`, `petition.txt`, `questions-presented.txt`):**
   - Petitioners (ON24, Inc., its officers/directors, and IPO underwriters, represented by Brian R. Matsui of Morrison & Foerster LLP) seek review of an unpublished Ninth Circuit memorandum disposition (`App. 1a–9a`, filed Jan. 12, 2026; rehearing denied Mar. 10, 2026) that reversed in part the Northern District of California's dismissal of Section 11 and Section 15 claims under the Securities Act of 1933.
   - The petition presents three questions:
     - **QP 1:** Whether an issuer violates Section 11(a) when its registration statement describes risks as hypothetical if those risks have not yet materialized into actual operational or financial harm (`Facebook, Inc. v. Amalgamated Bank`, No. 23-980, which was DIG'd in November 2024).
     - **QP 2:** Whether an omission violates Section 11(a) whenever it relates to a disclosed fact, or only when it renders an affirmative statement misleading under *Omnicare, Inc. v. Laborers District Council Construction Industry Pension Fund*, 575 U.S. 175 (2015), and *Macquarie Infrastructure Corp. v. Moab Partners, L.P.*, 601 U.S. 257 (2024).
     - **QP 3:** Whether an issuer can violate Item 303 of Regulation S-K—and thus Section 11(a)'s "required to be stated" prong—by failing to disclose immaterial facts as "known trends or uncertainties."
   - Crucially, the petition (`petition.txt` at pp. 4, 24–33, 35) emphasizes that the Ninth Circuit panel below relied on its recently published decision in *Sodha v. Golubowski* (`Robinhood Markets, Inc. v. Sodha`, No. 25-944) for its Section 11 omissions and Item 303 holdings, and explicitly asks the Court to **hold this petition if the Court grants certiorari in *Robinhood* (No. 25-944)** (`petition.txt` at p. 35: *"Accordingly, if the Court were to grant the petition in Robinhood, it should at minimum hold this petition pending a decision on the merits in Robinhood."*).

2. **Forward-Mode Context (Post-Snapshot Developments on `25-1376` and `25-944`):**
   Because `record/context.json` sets `mode: "forward"`, post-cutoff developments prior to any disposition are legitimate forward signals:
   - In `25-1376` (*ON24*), following the July 22, 2026 call for a response, respondent filed its Brief in Opposition on September 21, 2026, petitioners filed their Reply on October 6, 2026, and the petition was distributed a second time (`distribution_count: 2` in the live corpus row) for the **November 6, 2026 conference**.
   - In the lead related case, *Robinhood Markets, Inc. v. Sodha* (No. 25-944), the Court issued a CVSG on June 1, 2026 (`cvsg_date: "2026-06-01"` in the corpus). On **October 7, 2026**, the Solicitor General filed the United States' amicus brief in *Robinhood*, recommending that the Court **grant certiorari on Question 1** (rewritten to focus on whether Section 11(a)'s misleading-omissions clause requires a specific affirmative statement to be rendered misleading) and deny review on Question 2 (Item 303), while noting that *Robinhood* is the superior vehicle over *ON24*. *Robinhood* (`25-944`) is also distributed for the **November 6, 2026 conference**.

3. **Probability Calibration (`P(grant) = 0.25`):**
   - **Plenary grant in *ON24* (`~3–4%`):** Standalone plenary review in *ON24* is unlikely. Unlike *Robinhood* (which is a published opinion supported by multiple amici and a CVSG grant recommendation), *ON24* arises from a short, unpublished Ninth Circuit memorandum disposition (`App. 1a–9a`), drew zero amicus briefs, and centers heavily on fact-specific confidential-witness allegations that COVID-era customer churn had already begun before the February 2021 IPO. Moreover, the Court already DIG'd the "hypothetical risk factor" question in *Facebook v. Amalgamated Bank* (2024) due to fact-bound disputes over what had materialized, and *ON24* suffers from the same vehicle flaws on QP 1.
   - **Hold-and-GVR path via *Robinhood* (`~21–22%`):** Under the schema, `gvr` counts as a grant (`granted = 1`, `disposition` claim resolves true). For *ON24* to end in a GVR, three events must occur:
     1. The Court grants certiorari in *Robinhood* (No. 25-944) following the SG's partial-grant recommendation (`~65–70%` chance given the SG's recommendation to grant QP 1, though tempered by the SG's rewrite and vehicle objections raised by respondent).
     2. The Court holds *ON24* pending *Robinhood* rather than denying it outright (`~50%` conditional on a *Robinhood* grant). While the Ninth Circuit panel in *ON24* cited *Sodha* (`App. 6a, 8a`), its core rationale was that ON24's explicit statements ("historically retained customers," "LTV:CAC ratio," and hypothetical risk warnings) were plausibly misled by undisclosed ongoing customer churn (`App. 5a–8a`). If the Justices view *ON24* as turning on affirmative risk/retention statements that were rendered misleading under any standard (including the SG's standard in *Robinhood*), the Court may simply deny *ON24* at the November 6 conference or after one relist rather than holding it.
     3. Conditional on *Robinhood* being granted and *ON24* being held, *Robinhood* results in a vacatur or reversal that triggers a GVR of *ON24* (`~65%`).
   - Combining the plenary-grant path (`~3.5%`) and the hold-then-GVR path (`~21.5%`) yields `P(grant) = 0.25`. Because `0.25 < 0.50`, `granted = 0` and `predicted_disposition = "denied"` (the modal single outcome at `75%`).

### Secondary Claims and Distribution Rationales

- **`relist-increment` (`0.99`):** The cell's frozen context has `distribution_count: 1` as of `2026-07-22` (the day the response was requested). Once a response is requested, the petition is re-distributed for conference after the BIO arrives (and in fact the live corpus row confirms `distribution_count: 2` for the November 6, 2026 conference). As `predict.md` notes, on a `response-requested` cell `relist-increment` is all but certain and masked by the harness; I state `0.99`.
- **`cvsg-increment` (`0.02`):** The Court already issued a CVSG in *Robinhood* (`25-944`) and received the SG's brief on October 7, 2026. There is virtually no reason for the Court to issue a second CVSG in *ON24*.
- **`summary-disposition-route` (`0.85`):** Conditional on *ON24* being granted (`granted` or `gvr`), the overwhelming majority of that probability mass (`~21.5%` out of `25%`, or `~86%`) comes from a post-*Robinhood* GVR rather than a standalone plenary grant (`~14%`). Accordingly, I set `summary-disposition-route` to `0.85`.
- **`dissent-from-denial` (`0.03`) and `order-writers`:** Even if denied, an unpublished, fact-bound Ninth Circuit securities pleading decision is unlikely to draw a published dissent from denial, especially with *Robinhood* available on the same conference list to address the legal issue if four Justices want to reach it. I assign `0.03` to `dissent-from-denial` and small per-Justice probabilities in `order-writers` led by Thomas (`0.015`), Alito (`0.012`), and Gorsuch (`0.010`).
