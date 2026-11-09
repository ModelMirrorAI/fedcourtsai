# Predictor Rationale: *Paul Schultz v. H. Jason Gold* (No. 26A658, `evt-motion-disposition`)

## Summary of Forecast

- **Top-level `probability` / `interim-disposition`:** `0.01` (`granted = 0`, `predicted_disposition = "denied"`)
- **Procedural increments (`interim-v3`):**
  - `response-requested-increment`: `0.02`
  - `referral-increment`: `0.02`
  - `amicus-increment`: `0.01`
- **`big_case_score`:** `0.01`

## Base-Rate Anchoring

1. **Scored Interim Pool Base Rate (OT2016–OT2025):**
   From `metrics/statpack.md` ("The interim docket (applications)") and `metrics/statpack.json`, the scored baseline for an OT2026 interim application pools `finer_granted` over `finer_resolved` across the ten application-Terms strictly preceding OT2026 (`2016 <= T < 2026`). Summing the per-Term counts:
   - OT2025: `19 / 218`
   - OT2024: `18 / 189`
   - OT2023: `17 / 124`
   - OT2022: `9 / 103`
   - OT2021: `17 / 107`
   - OT2020: `27 / 133`
   - OT2019: `13 / 119`
   - OT2018: `14 / 113`
   - OT2017: `13 / 124`
   - OT2016: `9 / 107`
   - **Total pooled scored baseline:** `156 / 1337 = 11.67%` (`11.7%`), with `finer_unread = 0` in all ten Terms, well above the `INTERIM_BASE_RATE_MIN_RESOLVED = 50` floor. (As noted in `statpack.md`, parse coverage is uneven in earlier Terms—15 unparsed in OT2016 and 1 in OT2017—and the predicted reserve is selected higher on the escalation ladder than the raw cohort.)

2. **Applicant-Class and Capital-Marking Cut (`caption-v2`):**
   In `metrics/statpack.md` ("Substantive applications by applicant class", pooling the same ten prior Terms OT2016–OT2025 under `finer_*`), Applicant Paul Schultz (`"Paul Schultz, Applicant"`, `bCapitalCase: false`) falls in the **`private` / `unmarked`** cell:
   - **`private` / `unmarked` cell:** `63 / 906 = 7.0%` (`6.95%`).
   - **`private` row margin (`all`):** `73 / 1194 = 6.1%`.
   - **`unmarked` column margin (`all`):** `126 / 1021 = 12.3%`.
   We lean on the specific `private` / `unmarked` cell (`7.0%`, `n = 906`) as our primary demographic reference point before case-specific adjustments, because private non-capital applicants face a substantially lower grant rate than federal (`68.4%`, `39 / 57`) or state (`41.4%`, `24 / 58`) non-capital applicants.

## Case-Specific Evidence and Adjustments

1. **Provisioned Record and Document Status:**
   - Snapshot `2026-11-03.json` (`context.json`: `mode = "forward"`, `cut_kind = "arrival-position"`, `cut_anchor_index = 0`, `cutoff = "2026-11-03"`) shows that Paul Schultz, proceeding *pro se* (`Attorney: "Paul David Schultz"`, `State: "VA"`), submitted an application (`26A658`) for a stay to The Chief Justice on November 2, 2026, with Respondent listed as `H. Jason Gold`.
   - In `record/documents/documents.json`, `application.txt` (57 pages, fetched November 6, 2026) has `empty_text: true` and `ocr_derived: false` (an un-OCR'd image scan yielding whitespace only). We therefore rely on the docket metadata and lower-court records retrieved via the CourtListener MCP server and the corpus CLI.

2. **Lower-Court Posture and Upstream Docket Discrepancy:**
   - Although the Supreme Court docket snapshot (`2026-11-03.json`) lists `"LowerCourt": "United States Bankruptcy Appellate Panel for the 10th Circuit"` beside `"LowerCourtCaseNumbers": "(26-2404)"`, CourtListener records establish that `(26-2404)` is actually *In re: Paul Schultz*, No. 26-2404 in the **United States Court of Appeals for the Fourth Circuit** (`docket_id: 74925991`). That explains why the application was submitted to The Chief Justice (Circuit Justice for the Fourth Circuit, whereas Justice Gorsuch is Circuit Justice for the Tenth Circuit), why the applicant resides in Virginia, and why the respondent is H. Jason Gold, a Chapter 7 bankruptcy trustee in the Eastern District of Virginia. Companion application No. `26A657` (*Paul Schultz v. Kevin McCarthy*, arising from 4th Cir. No. `26-2406`) is properly recorded in the corpus as originating from `ca4`. We have noted this upstream `LowerCourt` metadata discrepancy in `flags.json` (`data-quality`, `info`).
   - In *In re: Paul Schultz*, No. 26-2404 (4th Cir. Oct. 22, 2026) (`opinion_id: 11512446`, Judges Wilkinson, King, and Rushing), the Fourth Circuit issued a two-page unpublished per curiam opinion denying Schultz's petition for a writ of mandamus seeking to disqualify District Judge Leonie M. Brinkema in Schultz's pending bankruptcy appeal (*Schultz v. Gold*, No. 1:26-cv-02804-LMB-IDD, E.D. Va., appealing orders in Adv. No. 26-01022, Bankr. E.D. Va.), to vacate the order denying recusal, and to reassign his bankruptcy appeal to a district judge from a different district court, while denying as moot his motions for a stay pending appeal.
   - Earlier, in *Paul Schultz v. H. Gold*, No. 25-2195 et al. (4th Cir. July 10, 2026) (`opinion_id: 11394602`), the Fourth Circuit resolved eight consolidated pro se appeals arising from the conversion of Schultz's Chapter 11 bankruptcy case to Chapter 7 and summary judgment for creditor Clear Sky Financial, LLC, affirming six appeals and dismissing two for lack of appellate jurisdiction. CourtListener dockets show more than twenty pro se appeals and mandamus petitions filed by Schultz in the Fourth Circuit arising out of the same bankruptcy proceedings.

3. **Downward Adjustment from `7.0%` to `1.0%`:**
   - Even within the `private` / `unmarked` substantive application bucket (`7.0%`), grants are heavily concentrated among represented parties presenting substantial constitutional or statutory questions where the Court calls for a response and refers the application to the full Court.
   - Here, (a) the applicant is proceeding *pro se* in a serial bankruptcy dispute, (b) the underlying Fourth Circuit order is an unpublished summary denial of a mandamus petition seeking judicial recusal in a still-pending district-court bankruptcy appeal, which has virtually zero chance of satisfying the *Hollingsworth v. Perry* / *Cheney* standards, and (c) as of the corpus row's latest live poll (`last_live_polled: "2026-11-09"`), no response has been requested (`response_requested: false`) and the application has not been referred (`referred_to_court: false`). Recent 2020s SCOTUS priors retrieved from the corpus (`26A637`, `26A644`, `26A636`, `26A602`, `26A612`, `26A619`) confirm that unreferred pro se stay applications with no response call are uniformly denied within days.
   - We therefore set `probability = 0.01` (`1.0%`), `response-requested-increment = 0.02`, `referral-increment = 0.02`, and `amicus-increment = 0.01`, with tiny `order-writers` probabilities (`0.002` for Chief Justice Roberts as Circuit Justice and `0.001` for each associate Justice).

## Key Uncertainties

Because `application.txt` is an un-OCR'd image scan (`empty_text: true`), we cannot inspect the exact text of Schultz's stay application to verify whether he raises any ancillary procedural claim beyond the Fourth Circuit's October 22, 2026 mandamus denial in No. 26-2404. However, given the pro se posture, the Fourth Circuit's opinion in No. 26-2404, and the absence of a response request, that uncertainty does not materially increase the probability of relief.
