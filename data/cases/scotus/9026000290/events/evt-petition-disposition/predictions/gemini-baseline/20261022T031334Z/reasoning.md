# Rationale for Certiorari Prediction — *Mihal Emberton v. Superior Court of California, City and County of San Francisco, et al.* (No. 26-290)

## 1. Executive Summary of Probability Calls

- **`probability` (`P(granted)`) / `claims.disposition`:** `0.003` (`granted: 0`, `predicted_disposition: "denied"`)
- **`claims.relist-increment`:** `0.015`
- **`claims.cvsg-increment`:** `0.001`
- **`claims.summary-disposition-route`:** `0.65` (conditional on grant)
- **`claims.dissent-from-denial`:** `0.002` (conditional on denial)
- **`big_case_score`:** `0.02`

---

## 2. Base-Rate Anchoring (`metrics/statpack.md`)

1. **Salience Band Anchor (`sal-v4`, `baseline`):**
   - Per `record/context.json`, this cell runs in `forward` mode for Term `2026` with `salience_version: "sal-v4"`, `band: "baseline"`, `signals_observable: true`, `distribution_count: 1`, `cvsg_date: null`, `response_requested: null`, and `amicus_briefs: null`.
   - In `metrics/statpack.md` under **"Segment base rate by salience band (sal-v4)"**, pooling the bracketed `reached` grant rate for the `baseline` band across the nine completed Terms strictly preceding OT 2026 (OT 2017–OT 2025) yields:
     - OT 2025: 3.9% ($n=1303$, ~50.8 grants)
     - OT 2024: 5.7% ($n=1271$, ~72.4 grants)
     - OT 2023: 5.9% ($n=1312$, ~77.4 grants)
     - OT 2022: 5.8% ($n=1192$, ~69.1 grants)
     - OT 2021: 5.6% ($n=1500$, ~84.0 grants)
     - OT 2020: 4.5% ($n=1739$, ~78.3 grants)
     - OT 2019: 4.6% ($n=1399$, ~64.4 grants)
     - OT 2018: 4.6% ($n=1524$, ~70.1 grants)
     - OT 2017: 4.7% ($n=1643$, ~77.2 grants)
     - **Pooled prior-Term `baseline` [reached] anchor:** $\approx 643.7 / 12,883 \approx \mathbf{5.00\%}$ (while the terminal `baseline` grant rate across the statpack is $1.2\%$ [$0.8\%$ granted + $0.4\%$ GVR], and `relist_bucket = 0` is $1.7\%$ [$1.2\%$ granted + $0.5\%$ GVR]).
2. **Originating Court Cut:**
   - Under **"Petitions by originating court (incl. state courts)"**, petitions from the `Court of Appeal of California, First Appellate District` have a 91.0% denial rate, 6.4% dismissal rate, and 2.6% grant rate ($n=78$ resolved), and petitions from the `Supreme Court of California` have a 90.7% denial rate, 9.3% dismissal rate, and 0.0% grant rate ($n=108$ resolved; $n=41$ in the reweighted table with 97.6% denied, 2.4% dismissed).

---

## 3. Case-Specific Adjustments from the Anchor

Starting from the $\approx 5.0\%$ `baseline` [reached] anchor for paid cert petitions at first distribution, strong downward adjustments are warranted based on the provisioned snapshot (`2026-10-22.json`), the provisioned filings (`petition.txt` and `questions-presented.txt`), and the prior federal court orders retrieved via CourtListener MCP (`Emberton v. San Francisco City Government`, No. 3:22-cv-05440-TSH, N.D. Cal.):

1. **No Response Filed and No CFR (`2026-10-22.json`):**
   - The petition was docketed September 3, 2026 with a response due October 5, 2026. Respondents allowed the deadline to lapse without filing a response, and the petition was distributed on October 21, 2026 for the November 6, 2026 conference without a call for a response (CFR). Under Supreme Court practice, a petition distributed for conference without a brief in opposition and without a CFR has a near-zero probability of being granted at that conference, and a very low probability of drawing a CFR/relist when filed *pro se*.
2. ***Pro Se* Petitioner Status:**
   - Although docketed on the paid appellate docket (`26-290`), petitioner Mihal Emberton is proceeding *pro se* (`petition.txt` cover page; `2026-10-22.json`). Empirical grant rates for *pro se* petitions—even paid ones—sit well below $0.5\%$.
3. **Severe Jurisdictional Defect (Lack of Finality under 28 U.S.C. § 1257(a)):**
   - As `petition.txt` (pages 1, 7–9, and Appendix A–B) discloses, petitioner seeks review of the California Supreme Court's March 25, 2026 one-sentence denial of review (No. S295215) and the California Court of Appeal's February 9, 2026 summary denial of an extraordinary writ petition (No. A175551).
   - That writ petition challenged an August 27, 2025 San Francisco Superior Court order (No. CGC-22-601288) sustaining San Francisco's demurrer to petitioner's Seventh Amended Complaint *with and without leave to amend*. Because leave to amend was granted in part and the challenge reached the appellate courts via a discretionary interlocutory writ petition (which was also flagged by the Court of Appeal for violating California Rules of Court 8.204(c)(1) and 8.74(a)(3)), there is no final judgment rendered by the highest state court under 28 U.S.C. § 1257(a).
4. **Prior Federal Adjudication and Absence of Any Doctrinal Split:**
   - CourtListener MCP records from the earlier removal of the very same state lawsuit (`3:22-cv-05440-TSH`, ECF Nos. 19, 35, 37) clarify the full procedural history:
     - In ECF No. 19 (Feb. 15, 2023), Magistrate Judge Thomas S. Hixson dismissed petitioner's Fourth Amendment, Equal Protection, Due Process, Title II, 31 U.S.C. § 6711(a), ICCPR, and 18 U.S.C. § 242 claims, explaining that visual observation of a front-yard fence, arbor, and fire table from a public thoroughfare is not a Fourth Amendment search under *California v. Ciraolo*, 476 U.S. 207, 213 (1986), and *Marshall v. Barlow's, Inc.*, 436 U.S. 307, 315 (1978), and that municipal code-violation notices are not a physical seizure of property under *Soldal v. Cook County*, 506 U.S. 56, 61 (1992).
     - In ECF No. 35 (June 13, 2023) and ECF No. 37 (July 21, 2023), the federal court dismissed the amended § 1983 claims without prejudice under *Younger v. Harris*, 401 U.S. 37 (1971), dismissed the civil RICO claim with prejudice, and remanded only the state-law claims to San Francisco Superior Court.
   - Petitioner's three Questions Presented in `questions-presented.txt` and `petition.txt` (asserting that plain-view doctrine conflicts with *Boyd*, *Katz*, *Horton*, and *Kyllo*; that municipal code notices violate *In re Winship*'s "no-evidence" rule and constitute extortion/racketeering; and that the City Attorney's Office is disqualified from defending city agencies) do not implicate any real split of federal or state high-court authority.

Combining these factors reduces $P(	ext{granted})$ from the $5.0\%$ band anchor to **`0.003`** (0.3%), leaving a tiny residual for an unexpected GVR or procedural order.

---

## 4. Rationale for Declared Claims and Stakes Score

- **`disposition` (`0.003`):** Matches top-level `probability` exactly, as required.
- **`relist-increment` (`0.015`):** Given that Respondents waived a response by silence, no amicus briefs were filed, and the petition suffers from threshold § 1257(a) finality and *pro se* vehicle defects, the probability that any chambers calls for a response or relists the case after the November 6, 2026 conference is very low (~1.5%).
- **`cvsg-increment` (`0.001`):** Practically zero; no federal statutory or executive interest is present in a local San Francisco fence/arbor/encroachment dispute.
- **`summary-disposition-route` (`0.65`):** Conditional on the remote event of a grant (`granted = 1`), the Court would be substantially more likely to dispose of the petition summarily in the cert order (e.g., a GVR to the California courts) than to schedule a *pro se*, unbriefed interlocutory state demurrer dispute for full merits briefing and oral argument. In `metrics/statpack.md`, across all modern cert petitions, GVRs account for $588 / (662 + 588) = 47.0\%$ of the grant family, and for an unbriefed *pro se* petition where no BIO was filed, a summary GVR is even more dominant conditional on a grant.
- **`dissent-from-denial` (`0.002`):** Conditional on denial, the likelihood of a recorded dissent or statement respecting denial is negligible (~0.2%) because of the interlocutory state-court posture and settled open-view Fourth Amendment facts.
- **`big_case_score` (`0.02`):** Scored decoupled from grant probability. Even if decided, the dispute turns on idiosyncratic pro se pleadings arising out of a single homeowner's front-yard fence, trellis, and gas-line permit dispute with San Francisco municipal departments, carrying minimal national legal, policy, or public significance.

---

## 5. Uncertainty and Discount Factors

- **Provisioned Inputs:** All provisioned files (`2026-10-22.json`, `context.json`, `documents.json`, `petition.txt`, `questions-presented.txt`) were present and readable with `empty_text: false` and `truncated: false`. No brief in opposition exists because Respondents filed none.
- **Residual Uncertainty:** The only material uncertainty is whether the Court could administratively dismiss the petition on a technical rule ground rather than entering a standard denial (`denied` vs. `dismissed`, which sits at ~1.2% in the `baseline` band), though neither affects the binary `granted = 0` axis.
