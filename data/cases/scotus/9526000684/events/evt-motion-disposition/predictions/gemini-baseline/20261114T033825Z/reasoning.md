# Rationale for Prediction — `scotus/9526000684` (`evt-motion-disposition`)

## Summary of Forecast Numbers

- **Top-level `probability` / `interim-disposition`:** `0.002` (`granted = 0`, `predicted_disposition = "denied"`)
- **`response-requested-increment`:** `0.015`
- **`referral-increment`:** `0.012`
- **`amicus-increment`:** `0.005`
- **`order-writers`:** `Roberts: 0.002`, all eight Associate Justices `0.001` each
- **`big_case_score`:** `0.03`

---

## 1. Provisioned Baseline and Conditioning State

This cell predicts at `stage: interim`, `moment: arrival` (`evt-motion-disposition`, opened `2026-11-10`) in `forward` mode. I read the provisioned baseline snapshot `2026-11-11.json` (`cut_kind: "arrival-position"`, `cut_anchor_index: 0`, `cutoff: "2026-11-11"`) and `record/context.json`. At the arrival cut:

- The docket carries a single proceeding entry on November 10, 2026: *"Application (26A684) for a stay, submitted to The Chief Justice."*
- Applicant Paul David Schultz appears *pro se* (contact details withheld in both `2026-11-11.json` and `application.txt`), arising from the Fourth Circuit (`No. 26-2405`).
- All escalation-ladder signals stand at their floor: `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`, and `bCapitalCase: false`. As expected for an interim cell, `band` is `null`.
- `record/documents/` stages `application.txt` (63 pages, `truncated: false`, `ocr_derived: true`, `contact_scrubbed: true` with 11 replacements and 0 residuals). Page App. 6a indicates that the multi-hundred-page appendix listed in the Table of Contents was filed separately as Clerk's Office material rather than inside the scanned 63-page main PDF.

### OCR and Caption Verification

Because `documents.json` flags `application.txt` as `ocr_derived: true`, I cross-checked key party names, docket numbers, statutory citations, and precedents against the provisioned snapshot, the corpus, and CourtListener MCP:

1. **Respondent name:** `2026-11-11.json` and `event.yaml` spell Respondent `"BOFK, N.A."`, whereas the application caption and body name `"BOKF, N.A."` CourtListener RECAP records for E.D. Va. No. `1:26-cv-01125` (*Schultz v. BOKF, N.A.*, docket `73338626`, assigned to Judge Leonie M. Brinkema) and Bankr. E.D. Va. No. `24-11959` (Dkt. 43 notice of appearance for BOKF, N.A.) confirm that `"BOKF, N.A."` is the bank's actual name and `"BOFK, N.A."` is a clerical transposition on the Supreme Court docket. Both spellings classify identically (`private`, `unmarked`).
2. **OCR character artifacts in `application.txt`:** The signature block reads `"Dated: November 38, 2026"` (an OCR misread of November 8/10; the snapshot confirms submission on `2026-11-10`); p. 29 line 1621 reads `"§ 362(c)(8)"` alongside `"§ 362(c)(3)"` on lines 1618 and 1630 (clearly `11 U.S.C. § 362(c)(3)`); p. 35 line 1791 reads `"17-18863-BFK"` immediately after `"17-13863-BFK"`; and p. 39 line 1906 reads `"Dkt. 18"` for Fourth Circuit stay motion `"Dkt. 13"` (confirmed at pp. 12, 19, and App. TOC item 4). None of these OCR artifacts creates ambiguity about the substance of the application.
3. **Lower-court and precedent verification:** CourtListener RECAP for Bankr. E.D. Va. `24-11959` confirms 836+ docket entries, including the October 22, 2026 emergency stay motion (`Dkt. 830`) and the October 29, 2026 docketed order on motion to stay (`Dkt. 833`), as well as roughly twenty Fourth Circuit dockets involving Applicant (`25-2195` through `26-2180`). CourtListener and `fedcourts query` also confirm Applicant's cited recent Supreme Court decisions, including *Clark v. Sweeney*, No. 25-52 (Nov. 24, 2025), *Margolin v. NAIJ*, No. 25-767 (May 26, 2026), *FCC v. Brown*, No. 26A476 (Oct. 14, 2026), and *Malliotakis v. Williams*, No. 25A914 (Mar. 2, 2026).

---

## 2. Base-Rate Anchoring (`metrics/statpack.md` and `metrics/statpack.json`)

In **"The interim docket (applications)"** (whose caption carries the updated scored-baseline wording: *"The rows below ground the interim stage's scored base rate"*), an OT2026 application (`26A684`) is scored against the unweighted `finer_granted / finer_resolved` rate pooled over the 10 strictly prior application-Terms (`2016 <= T < 2026`, OT2016–OT2025), excluding moot dismissals and counting partial grants as granted:

- Summing `finer_granted` and `finer_resolved` across OT2016–OT2025 in `statpack.json` (which matches the bottom-right total of **"Substantive applications by applicant class"** in `statpack.md`) yields **`156 / 1337 = 11.7%`** (`0.1167`), with `finer_unread = 0` in all ten Terms and `unparsed = 0` in OT2018–OT2025 (`1` in OT2017, `15` in OT2016). This clears `INTERIM_BASE_RATE_MIN_RESOLVED = 50` by a wide margin. (I do not anchor on the older `substantive_granted / substantive_resolved` columns printed in the per-Term Markdown table, which sum to `160 / 1363` over the same ten Terms.)
- Two structural caveats govern this `11.7%` pool: escalation-signal counts in the table are terminal/right-censored rather than as-at-arrival, and the scored reserve selects applications up the escalation ladder, whereas `11.7%` averages across federal, state, and private applicants alike.
- In **"Substantive applications by applicant class"** (`caption-v2` over OT2016–OT2025 `finer_*` counts), Applicant is a **`private`** individual in an **`unmarked`** (non-capital) docket. The `private × unmarked` cell is **`7.0% (63/906)`** (well above the 30-case floor; the `private` row margin is `6.1% (73/1194)` and the `unmarked` column margin is `12.3% (126/1021)`, the latter inflated by `federal × unmarked` at `68.4% (39/57)` and `state × unmarked` at `41.4% (24/58)`). I use the specific `private × unmarked` cell (`7.0%`, `n=906`) rather than the margins as my descriptive starting point, then adjust steeply downward to `0.002` (`0.2%`) based on the overwhelming case-specific and companion-case evidence below.

---

## 3. Case-Specific Adjustments Driving `P(granted) = 0.002`

1. **Immediate in-chambers denials of Applicant's two companion applications (`26A657` and `26A658`):**
   Corpus queries restricted to `--decided-before 2026-11-12` (on or before our `2026-11-11` snapshot date) surfaced two directly parallel substantive emergency applications filed by Paul David Schultz on November 6, 2026 out of contiguous Fourth Circuit dockets in the same bankruptcy litigation series:
   - **`26A657` (*Paul Schultz v. Kevin McCarthy*, `scotus/9526000657`)**, arising from CA4 No. `26-2406` (against the successor Chapter 7 trustee): `amicus_briefs: 0`, `response_requested: false`, `referred_to_court: false`, **denied on `2026-11-10`** (four days after filing) with no opinion.
   - **`26A658` (*Paul Schultz v. H. Jason Gold*, `scotus/9526000658`)**, arising from docket `26-2404` (against the prior bankruptcy trustee): `amicus_briefs: 0`, `response_requested: false`, `referred_to_court: false`, **denied on `2026-11-11`** (five days after filing) with no opinion.
   These two pre-cutoff companion dispositions show how Chief Justice Roberts's chambers treated Applicant's closely related emergency filings from the `26-2404 / 26-2405 / 26-2406` sequence: swift solo denial without calling for a response or referring to the full Court.

2. **Unexhausted and non-final posture below (Sup. Ct. R. 23.3):**
   Applicant has not filed a certiorari petition, nor has the Fourth Circuit finished acting on No. `26-2405`. According to the application itself, Applicant's Amended Combined Petition for Rehearing En Banc and Panel Rehearing (`Dkt. 14`, filed Oct. 28, 2026), emergency stay motion (`Dkt. 13-1`, Oct. 26), and motion to expedite (`Dkt. 15-1`, Oct. 29) remain **pending** in the Fourth Circuit, while the scheduled foreclosure date is **December 17, 2026**—more than five weeks after submission. Furthermore, Judge Brinkema denied Applicant's Rule 8007(b) stay motion *without prejudice* (`1:26-cv-01125`, Dkt. 11) before the Bankruptcy Court entered its October 28/29 stay denial (`Bankr. Dkt. 833`), leaving ordinary Rule 8007(b) renewal in the District Court and the pending Fourth Circuit stay motion available below.

3. **Zero realistic prospect of certiorari or reversal under `Hollingsworth` / `Nken` / `Cheney`:**
   To obtain a stay or All Writs Act injunction in aid of prospective jurisdiction, Applicant must demonstrate a reasonable probability of four votes for certiorari and a fair prospect of reversal—or an "indisputably clear" right for injunctive relief (*Hollingsworth v. Perry*, 558 U.S. 183, 190 (2010); *Ohio Citizens for Responsible Energy, Inc. v. NRC*, 479 U.S. 1312, 1313 (1986) (Scalia, J., in chambers)). Here:
   - Fourth Circuit No. `26-2405` was an unpublished per curiam denial of **mandamus** seeking Judge Brinkema's disqualification under 28 U.S.C. § 455(a). Under *Cheney v. U.S. Dist. Court*, 542 U.S. 367, 380–81 (2004), mandamus is unavailable where post-judgment appellate review is adequate, and § 455(a) rulings are reviewable on appeal after the District Court decides the bankruptcy appeal.
   - Applicant's reliance on *United States v. Sineneng-Smith*, 590 U.S. 371 (2020), *Clark v. Sweeney* (`25-52`), and *Margolin v. NAIJ* (`25-767`) is misplaced: those cases involved appellate panels reversing judgments on unbriefed claims, whereas a district judge evaluating an unopposed § 455(a) recusal motion has an independent duty to apply *Liteky v. United States*, 510 U.S. 540 (1994), and is not required to adopt the movant's framing simply because the opposing party filed no response.
   - Finally, Applicant's broader "Four-Layer Shield" argument centers on junior/disputed creditor Clear Sky Financial, LLC and Richard Oppenheim, Jr., whereas Respondent **BOKF, N.A.** is a separate first-lien residential mortgage creditor that obtained § 362(d)(1) stay relief (`Bankr. Dkt. 625`) after an evidentiary record showing post-petition payment default and lack of equity. Enjoining BOKF's state-law foreclosure from inside a recusal-mandamus proceeding is doctrinally implausible.

*(Per prompt rules, I do not discount `probability` for the chance that the Fourth Circuit denies rehearing or acts below in a way that moots the application first; `0.002` prices P(grant in whole or in part | not dismissed or denied as moot).)*

---

## 4. Ladder Increments, Order Writers, Big-Case Score, and Uncertainties

- **`response-requested-increment` (`0.015`) and `referral-increment` (`0.012`):** Calling for a response is far more common than granting relief on private applications, and a Circuit Justice occasionally requests a brief response when an applicant alleges an upcoming foreclosure date. However, because `26A657` and `26A658` both resolved in chambers within 4–5 days with neither a response request nor a referral, both increments sit just above 1%.
- **`amicus-increment` (`0.005`):** With a short expected chambers lifespan and a purely individual *pro se* bankruptcy record, third-party amicus submissions (whether accepted or submitted-only) are near zero.
- **`order-writers` (`Roberts: 0.002`, others `0.001`):** Separate writings on unreferred *pro se* chambers denials are exceedingly rare; Chief Justice Roberts receives `0.002` as Circuit Justice and each Associate Justice `0.001`.
- **`big_case_score` (`0.03`):** Decoupled from grant odds, the case involves significant personal stakes for one *pro se* homeowner/debtor but carries virtually no national policy, institutional, or doctrinal significance if decided.
- **Uncertainties:** We do not have the separately lodged Clerk's Office appendix volumes (`App. 7a–326a`), so lower-court orders are read through Applicant's descriptions in `application.txt` as cross-checked against CourtListener RECAP docket metadata. Even under the most charitable reading of those descriptions, the procedural posture (pending Fourth Circuit rehearing, mandamus review of § 455(a) recusal, *pro se* serial bankruptcy appeals, and companion denials in `26A657` and `26A658`) leaves almost no room for Supreme Court interim relief.
