# Predictor Rationale: *Frank Parasmo v. United States* (No. 26-377)

## Summary of Forecast

- **Top-level call:** `granted = 0` (`predicted_disposition = "denied"`), `probability = 0.11` (`confidence = 0.78`).
- **Conditioning state (`context.json`):** `mode = "forward"`, `band = "baseline"` (`salience_version = "sal-v4"`), `distribution_count = 1`, `cvsg_date = null`, `term = 2026`, `input_snapshot = "2026-10-05.json"`.

## Base-Rate Anchor (`metrics/statpack.md`)

Per the cert-stage anchoring rules, we anchor on the `baseline` band's bracketed `reached` grant rate in the **"Segment base rate by salience band (sal-v4)"** table, pooled across all rendered Terms strictly preceding OT2026 (OT2017 through OT2025):

- **OT2025:** 4.0% (`n = 1314`)
- **OT2024:** 5.9% (`n = 1274`)
- **OT2023:** 5.9% (`n = 1312`)
- **OT2022:** 5.9% (`n = 1196`)
- **OT2021:** 5.7% (`n = 1500`)
- **OT2020:** 4.5% (`n = 1740`)
- **OT2019:** 4.7% (`n = 1399`)
- **OT2018:** 4.8% (`n = 1529`)
- **OT2017:** 4.9% (`n = 1649`)

Pooling across OT2017–OT2025 yields `659.44 / 12,913 = 5.11%` (**5.1%**).

Cross-checking the marginal cuts in `metrics/statpack.md`:
- **Modern discretionary-cert petitions overall:** `692` granted (1.5%) + `590` GVR (1.3%) = **2.9%** grant-family rate over `44,777` resolved petitions.
- **Originating circuit (`ca2`):** In the modern cert petitions by originating circuit table (denial-reweighted), `ca2` has `n = 2,070` resolved with **2.7% granted + 2.4% GVR = 5.1%** grant-family rate (`92.5%` denied, `2.5%` dismissed).
- **Relist count (paid scored segment):** Terminal `relist_bucket = 0` (`n = 10,203` resolved) has a **1.8%** grant-family rate (`1.3%` granted, `0.5%` GVR); `relist_bucket = 1` (`n = 2,538` resolved) rises to **13.7%** (`8.5%` granted, `5.2%` GVR); `relist_bucket = 2` (`n = 495` resolved) reaches **41.2%** (`28.3%` granted, `12.9%` GVR). Because this cell is at the `response-requested` moment, the petition is guaranteed to receive at least one additional distribution once the Brief in Opposition arrives.
- **Amicus count (paid scored segment):** Currently `0` amicus briefs are on the docket (`cert_amicus = 0` has a **3.8%** terminal grant-family rate: `2.0%` granted + `1.8%` GVR over `n = 11,109` resolved).

## Case-Specific Adjustments from the 5.1% Anchor

Starting from the **5.1%** `baseline` `[reached]` prior-Term anchor, we adjust upward to **11.0% (`0.11`)** based on the interaction of strong upward signals and substantial vehicle/posture headwinds:

### 1. Upward Adjustments (+8.5 percentage points)

1. **Call for Response (`moment: response-requested`) before the First Conference:** After the Solicitor General waived the right to respond on September 28, 2026, and the petition was distributed on September 30, 2026 for the October 16, 2026 Conference, the Court called for a response on October 5, 2026 (`2026-10-05.json`). While a Call for Response is a relatively low threshold—requiring only a single Justice's request—it filters out the large majority of `baseline` petitions that are denied on waiver at the first conference and guarantees that the petition will return to conference with full adversarial briefing.
2. **Published 2-1 Second Circuit Split with a Detailed Dissent:** In *United States v. Parasmo*, 176 F.4th 220 (2d Cir. May 19, 2026) (`appendix.txt`, Pet. App. 1a–44a), the panel unanimously held that the district court's pre-*Ruan* jury instruction on good faith under 21 U.S.C. § 841(a) was erroneous because it instructed the jury to apply an objective rather than subjective standard of intent. Judge Robinson dissented at length (`appendix.txt`, Pet. App. 31a–44a), arguing that subjective intent was the sole contested issue at trial, that the prosecution repeatedly told the jury in summation that the standard "has to be reasonable, and is not subjective" (Pet. App. 39a), that the jury returned a split verdict (acquitting on 3 of 35 counts), and that Dr. Parasmo's treatment records, specialist referrals, tapering efforts, and lack of "pill mill" characteristics (no cash kickbacks, fake patients, or unexamined prescriptions) provided ample evidence from which a properly instructed jury could have acquitted.
3. **Experienced Supreme Court Counsel and Doctrinal Framing:** Represented by Neal Katyal, Colleen Roh Sinzdak, and William Havemann of Milbank LLP (`petition.txt`), Petitioner frames the case around both a 4-1 post-*Ruan* harmless-error split—contrasting the Second Circuit's affirmance with reversals in *United States v. Kahn*, 58 F.4th 1308 (10th Cir. 2023), *United States v. Duldulao*, 87 F.4th 1239 (11th Cir. 2023), *United States v. Smithers*, 92 F.4th 237 (4th Cir. 2024), and *United States v. Qureshi*, 121 F.4th 1095 (5th Cir. 2024)—and broader tension under *Neder v. United States*, 527 U.S. 1, 17–19 (1999), and *Erlinger v. United States*, 602 U.S. 821, 842 (2024), over whether appellate judges may weigh the government's evidence against plausible defense evidence on a contested element.

### 2. Downward Counter-Weights (-2.6 percentage points)

1. **Fact-Bound Harmlessness Characterization by the Solicitor General:** Because the snapshot stops on the day the Court called for a response (`2026-10-05.json`), no Brief in Opposition has been filed yet. However, the Second Circuit majority opinion (`appendix.txt`, Pet. App. 11a–26a & n.2) clearly previews the response: all circuits recite the same *Neder* standard ("clear beyond a reasonable doubt that a rational jury would have found the defendant guilty absent the error"), and circuits that vacated convictions in *Duldulao* and *Kahn* have also found *Ruan* errors harmless when the record evidence of subjective knowledge was overwhelming (e.g., *United States v. Heaton*, 59 F.4th 1226, 1242 (11th Cir. 2023)). The majority highlighted stark patient-specific evidence—such as Dr. Parasmo continuing to prescribe 30-mg oxycodone to a patient who tested negative for oxycodone six times over 18 months after the patient's sister threatened to report him because the patient was selling the pills (Pet. App. 22a–23a), and continuing to prescribe after overdose hospitalizations and provider warnings (Pet. App. 13a–17a). The Court is historically reluctant to grant certiorari to referee fact-intensive applications of harmless-error review to a multi-week trial record.
2. **Fading Transitional Posture of Pre-*Ruan* Instructional Errors:** *Ruan* was decided in June 2022. Trials conducted after June 2022 incorporate *Ruan*'s subjective mens rea instruction, meaning the specific post-*Ruan* harmless-error question affects only a dwindling tail of pre-2022 trials still on direct appeal.
3. **Absence of En Banc Review or Amicus Support:** Petitioner did not seek rehearing en banc in the Second Circuit (`petition.txt` at 1), where intracircuit tension with *United States v. Pabisz*, 936 F.2d 80 (2d Cir. 1991), and *United States v. Tureseo*, 566 F.3d 77 (2d Cir. 2009), could have been addressed, and no amicus briefs have been filed.

## Secondary Claims Rationale

- **`relist-increment` (`0.98`):** Because the petition was distributed once on September 30, 2026 (`distribution_count = 1`) and pulled when the Court requested a response on October 5, 2026, it will almost certainly be distributed again once the Solicitor General files the Brief in Opposition (masked by the harness on `response-requested` cells for this reason).
- **`cvsg-increment` (`0.0`):** The United States is the respondent; a CVSG is impossible.
- **`summary-disposition-route` (`0.15`):** Conditional on a grant, plenary review of the *Neder* contested-element question is much more likely (`0.85`) than a summary reversal or GVR (`0.15`), as there is no pending Supreme Court companion case for a GVR hold and the factual record is contested between the panel majority and dissent.
- **`dissent-from-denial` (`0.08`) and `order-writers`:** Conditional on denial, the combination of Judge Robinson's detailed dissent, the 80-year-old physician's prison sentence, and the *Erlinger*/*Neder* Sixth Amendment framing creates a realistic ~8% chance of a separate writing (most likely by Justice Gorsuch at `0.035`, Justice Sotomayor at `0.025`, or Justice Jackson at `0.020`).

## Uncertainty and Limitations

Our primary uncertainty is how forcefully the Solicitor General's forthcoming Brief in Opposition will defend the Second Circuit majority's count-by-count harmlessness analysis (note that the Second Circuit majority focused primarily on five patients across 32 counts of conviction). Our live check of `supremecourt.gov` confirmed that as of October 29, 2026, the docket remains at the October 5, 2026 Call for Response entry with the response due November 4, 2026. Also, the CourtListener MCP server returned an HTTP 429 daily rate-limit error on our query, so we relied on the provisioned petition and appendix (which include the complete Second Circuit majority and dissenting opinions) and the local corpus tooling.
