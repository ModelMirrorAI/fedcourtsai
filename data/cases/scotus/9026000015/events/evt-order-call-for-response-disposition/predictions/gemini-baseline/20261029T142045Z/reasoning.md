# Predictor Reasoning: *Gary Perez, et al. v. City of San Antonio, Texas* (No. 26-15)

## Summary of Forecast
- **Predicted Disposition:** `denied` (`granted: 0`)
- **Probability of Grant (`probability` / `disposition`):** `0.42`
- **Confidence:** `0.65`
- **Big Case Score:** `0.72`

## 1. Provisioned Record and Procedural Posture

This cell predicts `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`, `mode: forward`). I read the provisioned snapshot `record/snapshots/2026-07-31.json` (`snapshot_date: 2026-07-31`, `cutoff: 2026-07-31`, `cut_kind: date`) and all provisioned documents in `record/documents/` (`questions-presented.txt`, `petition.txt`, `appendix.txt`, and `documents.json`; none had `empty_text: true` or `ocr_derived: true`, though both `petition.txt` and `appendix.txt` carry pipeline truncation notes within their appendix portions to fit the 150,000-character cap).

From `2026-07-31.json` and `context.json`:
- Petitioners Gary Perez and Matilde Torres, ceremonial leaders of the Lipan Native American Church, are represented by Prof. Steven T. Collis of the University of Texas School of Law Clinic.
- The petition was filed on June 26, 2026 (docketed July 2, 2026).
- Ten cert-stage amicus briefs/filings are already listed on the docket snapshot under `Other` (`CatholicVote.org`, `National Religious Broadcasters`, `The Jewish Coalition for Religious Liberty`, `Several Religious Organizations`, `Ethics and Public Policy Center`, `The Comanche Nation`, `Human Rights Defense Center`, `International Council of Thirteen Indigenous Grandmothers and Notre Dame Law School Religious Liberty Clinic`, `Indigenous Religion Scholars`, `Association on American Indian Affairs`, `The Sikh Coalition et al.`, and `Religious Freedom Institute`—12 counsel-of-record entries for amici on the snapshot).
- Respondent City of San Antonio waived its right to respond on July 21, 2026.
- The petition was distributed on July 29, 2026 for the September 28, 2026 conference (`distribution_count: 1`).
- On July 30, 2026, the Court called for a response (`Response Requested. (Due August 31, 2026)`). No response is on the record at the July 31 cutoff, and I do not infer what the BIO will argue.

## 2. Base-Rate Anchoring (`metrics/statpack.md`)

1. **Overall Modern Cert Base Rate:** In the `Modern discretionary-cert petitions by disposition` table (denial-reweighted live/historical slice, $N = 44,777$ resolved), the base rate is `denied` 95.1%, `dismissed` 2.1%, `granted` 1.5%, and `gvr` 1.3% (grant family $\approx 2.9\%$). For `ca5` originating petitions ($N = 5,399$ resolved), the rate is `denied` 94.6%, `gvr` 2.1%, `granted` 1.7%, `dismissed` 1.6% (grant family $3.8\%$).
2. **Salience Band Anchor (`sal-v4`):** `record/context.json` freezes `band: "baseline"` under `salience_version: "sal-v4"` as of the July 31, 2026 cutoff. Per the prompt contract, I anchor on the `baseline` band's bracketed `reached` rate pooled across the 9 rendered Terms strictly preceding OT2026 (OT2017–OT2025) in the `Segment base rate by salience band (sal-v4)` table:
   - OT2025: $4.0\%$ ($n=1314$, $\approx 52.6$ grants)
   - OT2024: $5.9\%$ ($n=1274$, $\approx 75.2$ grants)
   - OT2023: $5.9\%$ ($n=1312$, $\approx 77.4$ grants)
   - OT2022: $5.9\%$ ($n=1196$, $\approx 70.6$ grants)
   - OT2021: $5.7\%$ ($n=1500$, $\approx 85.5$ grants)
   - OT2020: $4.5\%$ ($n=1740$, $\approx 78.3$ grants)
   - OT2019: $4.7\%$ ($n=1399$, $\approx 65.8$ grants)
   - OT2018: $4.8\%$ ($n=1529$, $\approx 73.4$ grants)
   - OT2017: $4.9\%$ ($n=1649$, $\approx 80.8$ grants)
   - **Pooled strictly-prior `baseline [reached]` anchor (OT2017–OT2025):** $\approx 659.5 / 12,913 = 5.11\%$.
3. **Signal Cuts (Amicus & Call for Response):**
   - Although the snapshot is frozen at `band: "baseline"` before the BIO is filed and before post-BIO relists occur, the `Cert petitions by amicus-brief count (paid scored segment)` table shows that petitions with `2+` cert amicus briefs ($n = 1,449$ resolved) have a grant rate of `18.4%` plus `4.5%` GVR (`22.9%` grant family), compared to `3.8%` for `0` amici ($n = 11,109$). Here, the petition attracted a dozen diverse cert-stage amicus groups before the response was even requested.
   - Furthermore, the Court called for a response on July 30, 2026—just one day after initial distribution and nearly two months before the September 28 conference—indicating immediate interest from at least one chambers.

## 3. Case-Specific Adjustments

### Upward Adjustments (from 5.1% anchor toward 42%)
1. **Six-Judge Fifth Circuit En Banc Dissent:** Following panel opinions (163 F.4th 110) where Judge Higginson dissented three times, the Fifth Circuit denied rehearing en banc by an 11–6 vote (168 F.4th 345). Judge Oldham authored a forceful dissent joined by Chief Judge Elrod and Judges Smith, Higginson, Willett, and Ho, and Judge Ho authored an additional solo dissent. A six-judge en banc dissent from the Fifth Circuit featuring Judges Oldham, Ho, Willett, Elrod, Smith, and Higginson is one of the strongest lower-court signals for Supreme Court cert attention.
2. **Massive Cert-Stage Amicus Coalition (12 Amicus Filings):** The snapshot shows 12 distinct amicus representations spanning conservative Christian and Jewish advocacy groups (`Ethics and Public Policy Center`, `Religious Freedom Institute`, `National Religious Broadcasters`, `Jewish Coalition for Religious Liberty`, `CatholicVote.org`), minority religious groups (`Sikh Coalition et al.`), tribal nations (`Comanche Nation`, `Association on American Indian Affairs`), and clinics (`Notre Dame Religious Liberty Clinic`).
3. **Compelling Strict-Scrutiny Record on QP 2:** Even setting aside the difficult *Lyng* question on sacred-site burdens, QP 2 presents a clean and factually stark strict-scrutiny issue under both the First Amendment (*Fulton v. City of Philadelphia*, 593 U.S. 522 (2021), where the City obtained tree-preservation variances for itself) and TRFRA: the City admitted in its answer and testimony that it never studied whether it could achieve its retaining-wall repair goals while accommodating Petitioners' religious exercise because reconsidering its pre-approved cantilever design "would take time and money." That admission directly implicates the circuit split between the First, Second, Third, Eighth, Ninth, and D.C. Circuits (which require pre-litigation consideration of less-restrictive alternatives) and the Fifth, Seventh, Tenth, and Eleventh Circuits.

### Downward / Moderating Factors (why P(grant) stays below 50% at 0.42)
1. **The *Apache Stronghold* / *Lyng* Shadow:** In May 2025, the Court denied certiorari in *Apache Stronghold v. United States*, No. 24-291, 145 S. Ct. 1480 (2025) (corpus `scotus/70377102`), after 18 distributions, over a dissent from denial by Justice Gorsuch joined by Justice Thomas (with Justice Alito recused). While Justice Alito is not recused here (he granted the time extension in `25A1261`), getting a fourth and fifth vote to revisit *Lyng v. Northwest Indian Cemetery Protective Ass'n*, 485 U.S. 439 (1988), as applied to government management of its own land/park trees remains uncertain.
2. **Dual State-Law (TRFRA) and Interlocutory Preliminary-Injunction Posture:** Much of the strict-scrutiny analysis below turned on the Texas Religious Freedom Restoration Act (TRFRA) and the Texas Constitution's Religious Services Amendment (certified to the Texas Supreme Court, 715 S.W.3d 709), and the appeal arises from a preliminary-injunction denial where part of the relief (access to the Sacred Area) was granted and the cross-appeal dismissed. Respondents in opposition will likely argue that state-law TRFRA questions and fact-bound engineering disputes over tree roots and retaining walls make this a poor vehicle.

Weighing the extraordinary amicus support (12 filings), the 6-judge Fifth Circuit en banc dissent, and the immediate call for a response against the *Apache Stronghold* denial and the state-law/preliminary-injunction vehicle hurdles, I place `probability` at **0.42** (`granted: 0`, `predicted_disposition: "denied"`).

## 4. Claims and Distribution Rationale

- **`disposition`: `0.42`** — Matches top-level `probability`.
- **`relist-increment`: `0.99`** — Masked on `response-requested` cells because once the requested BIO is filed, the petition will almost certainly be distributed again for a subsequent conference.
- **`cvsg-increment`: `0.04`** — Very low probability of a CVSG because the respondent is a municipality and no federal statute or federal land is involved.
- **`summary-disposition-route`: `0.08`** — Conditional on a grant, plenary review is far likelier (`92%`), with a small (`8%`) chance of a summary vacatur/remand on the strict-scrutiny analysis.
- **`dissent-from-denial`: `0.55`** — Conditional on denial, there is a high (`55%`) chance of a published dissent from denial, given Justice Gorsuch's recent dissent in *Apache Stronghold* and the six-judge Fifth Circuit dissent below.
- **`order-writers`:** Justice Gorsuch (`0.45`) is by far the likeliest author of a dissent from denial (as in *Apache Stronghold*), followed by Justice Alito (`0.16`) and Justice Thomas (`0.14`).

## 5. Retrieval Note

During investigation, I attempted one CourtListener MCP `search` call for the lower-court Fifth Circuit opinion, which returned HTTP 429 (daily rate limit exceeded). Per the prompt instructions, I degraded gracefully without retrying and relied on the complete Fifth Circuit panel and en banc opinions reproduced in `record/documents/petition.txt` and `appendix.txt`, alongside `uv run fedcourts query` against the local corpus service.
