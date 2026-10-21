# Rationale for Prediction: *David M. Scanlan, Secretary of State of New Hampshire, et al. v. Coalition for Open Democracy* (No. 26A512)

## 1. Summary of Numbers

- **Top-level `probability` (`interim-disposition`):** `0.22` (`granted: 0`, `predicted_disposition: "denied"`, `confidence: 0.72`)
- **Declared `interim-v1` Claims:**
  - `interim-disposition`: `0.22`
  - `response-requested-increment`: `0.85`
  - `referral-increment`: `0.75`
  - `amicus-increment`: `0.30`
- **`big_case_score`:** `0.55` (election-law *Purcell* stay application brought by New Hampshire state officials regarding student ID verification ahead of the November 2026 general election, moderated by the narrow scope of the injunction, which upheld HB 323 and affected only discretionary safety-valve guidance).
- **Inputs Consulted:** Provisioned snapshot `2026-10-15.json`, `record/context.json`, provisioned `record/documents/application.txt` (`documents.json` shows 18 pages, `empty_text: false`, `truncated: false`), `metrics/statpack.md`, corpus queries via `fedcourts query`, and lower-court dockets/filings via CourtListener MCP (`nhd` Docket 1:26-cv-00647 and `ca1` Docket 26-2132).

---

## 2. Base-Rate Anchoring (`metrics/statpack.md` — Interim Docket)

Per `.github/prompts/predict.md` (*Stage: interim*), an interim cell anchors on **"The interim docket (applications)"** section of `metrics/statpack.md`, pooling `granted` over `resolved (subst.)` across the ten application-Terms strictly preceding this case's Term (`2026 - 10 <= T < 2026`, i.e., Terms 2016–2025):

- **2025:** 17 granted / 226 resolved (`7.5%`, `unparsed: 0`)
- **2024:** 16 granted / 194 resolved (`8.2%`, `unparsed: 0`)
- **2023:** 18 granted / 127 resolved (`14.2%`, `unparsed: 0`)
- **2016–2022:** 0 resolved (`unparsed` spans all applications in those Terms)
- **Pooled Strictly-Prior Substantive Base Rate (Terms 2016–2025):** $(17 + 16 + 18) / (226 + 194 + 127) = 51 / 547 = \mathbf{9.32\%}$ (clearing the pre-registered floor of `INTERIM_BASE_RATE_MIN_RESOLVED = 50`).

Note on coverage and selection: as `metrics/statpack.md` cautions, Terms 2016–2022 have `unparsed` counts equal to their total applications, so the 547-application pool comes from OT2023–OT2025 (`unparsed: 0`). In addition, `record/context.json` shows `band: null` (the normal state for an interim application), `response_requested: false`, `referred_to_court: false`, and `amicus_briefs: 0` at the `arrival-position` cut (`2026-10-15`).

---

## 3. Case-Specific Adjustments from the `9.32%` Anchor

### Upward Adjustments (`+18%` to `~27%`)
1. **State Officials Invoking *Purcell* Ahead of a Federal Election:**
   Unlike the average substantive stay application (which includes many pro se or private civil/criminal stay requests that are summarily denied), this application is brought by a State Secretary of State and Attorney General invoking *Purcell v. Gonzalez*, 549 U.S. 1 (2006), regarding an October 2 preliminary injunction entered roughly one month before the November 3, 2026 general election. In September 2026 alone, the Court granted two election-related stays (*People Not Politicians v. Onder*, 609 U.S. ___ (Sept. 25, 2026), and *National Republican Congressional Committee v. Brown*, 609 U.S. ___ (Sept. 4, 2026)), and Justices Thomas, Alito, and Gorsuch treat *Purcell* as a near-categorical bar on late federal-court election injunctions.

### Downward Adjustments (`-5%` to final `0.22`)
Despite the strong *Purcell* framing in `application.txt`, examining the lower-court orders and First Circuit stay briefing retrieved via CourtListener MCP reveals four substantial weaknesses that make a stay denial much more likely than in *Onder* or *Brown*:

1. **Unexhausted First Circuit Stay Motion:**
   Applicants initially filed an improper stay motion in the First Circuit on October 5 without moving in the district court first, which the First Circuit denied without prejudice under Fed. R. App. P. 8(a)(1)(A). After Judge Laplante denied a stay on October 7 (Dkt. 72), Applicants renewed their First Circuit stay motion, and reply briefing closed on Saturday, October 10. Applicants then filed in the Supreme Court on Thursday, October 15—after giving the First Circuit panel less than five days to rule.
2. **No State Statute Was Enjoined:**
   Judge Laplante **upheld** New Hampshire HB 323 (which removed student IDs from RSA 659:13, II(a)'s list of photo IDs that ballot clerks must automatically accept). The narrow preliminary injunction applies **only** to the Secretary's April 23, 2026 press release ("Directive"), which instructed checklist supervisors that they could not even consider a student ID alongside other evidence under the statutory "safety valves" for registration (RSA 654:12, I(d)(4), allowing *"any other evidence"*) and obtaining a ballot (RSA 659:13, I(c)(3)).
3. **Waiver / Contradiction Below on the State's Statutory Argument:**
   In denying a stay pending appeal (Dkt. 72 at 2–3 & n.15), Judge Laplante found that the State's central legal argument—that SB 223's addition of the word "only" to RSA 659:13, II(a) limits the supervisor safety valves—was **raised for the first time in the motion to stay** and directly contradicted the State's own pre-injunction written Record Supplement (Dkt. 60), where the State represented that a supervisor could consider unlisted documents (such as a marriage certificate) under the safety valve. Under *Merrill v. Milligan*, 142 S. Ct. 879, 880–81 (2022) (Kavanaugh, J., concurring), and *Hollingsworth v. Perry*, 558 U.S. 183, 190 (2010), the median Justices (Roberts, Kavanaugh, Barrett) are unlikely to grant emergency relief to rescue a forfeited reading of state law when no statute was enjoined.
4. **Prior Implementation Inverts *Purcell*:**
   Immediately after the October 2 injunction, the Secretary updated his public website ("pursuant to court order, supervisors may consider a student identification card along with other available evidence") and distributed revised instructions to local officials in time for the October 6 Franklin municipal election. Moreover, ballot design, printing, and mailing are completely unaffected. As the First Circuit held in a parallel New Hampshire election case five weeks earlier (*New Hampshire Youth Movement v. Scanlan*, No. 26-1750, 2026 WL 2620381 (1st Cir. Sept. 4, 2026)), once the Secretary has posted revised instructions on which voters rely, granting a stay on the eve of the election would force a *second* reversal of public guidance and create the very voter confusion *Purcell* seeks to prevent.

---

## 4. Rationale for Increment Claims and Uncertainties

- **`response-requested-increment` (`0.85`):** State-official emergency applications invoking *Purcell* almost always trigger an expedited call for a response from the Circuit Justice unless mooted or denied immediately on procedural grounds (such as the pending First Circuit stay motion).
- **`referral-increment` (`0.75`):** Once a response is requested and filed in a state-official election stay application, Circuit Justices refer the application to the full Court in the vast majority of cases (in `metrics/statpack.md`, 347 of 633 resolved substantive applications were referred to the Court, and the rate is much higher among state-official applications that draw a response request). There remains a ~`0.25` chance that Justice Jackson acts alone or the application is resolved/withdrawn after a First Circuit ruling without full-Court referral.
- **`amicus-increment` (`0.30`):** In `metrics/statpack.md`, 99 of 642 substantive applications (`15.4%`) attract at least one amicus brief. Because election-law stay applications attract somewhat higher amicus participation from political committees or voting-rights groups than the average stay application, I adjust upward to `0.30`, capped by the rapid timeline and narrow state-law focus.
- **Key Uncertainties:** The main uncertainty is whether two of Justices Roberts, Kavanaugh, and Barrett view *Purcell* as mechanically barring any October federal-court order touching election administration even where only an executive press release was enjoined and already revised on the Secretary's website. That tail risk accounts for the `0.22` grant probability.
