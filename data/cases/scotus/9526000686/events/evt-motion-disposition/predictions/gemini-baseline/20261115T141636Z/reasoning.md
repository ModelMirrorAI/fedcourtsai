# Predictor Rationale — `scotus/9526000686` (`evt-motion-disposition`)

## Summary of Forecast

- **Top-level call:** `granted = 0`, `predicted_disposition = "denied"`, `probability = 0.008` (`P(granted in whole or in part | not moot)`).
- **Declared `interim-v3` claims:**
  - `interim-disposition`: `0.008`
  - `response-requested-increment`: `0.08`
  - `referral-increment`: `0.94`
  - `amicus-increment`: `0.03`
- **`big_case_score`:** `0.22`

---

## 1. Record and Retrieval Inputs Used

This is a `forward`-mode interim cell at `moment: arrival` (`cut_kind: "arrival-position"`, `cut_anchor_index: 0`, `cutoff: "2026-11-15"`). I read the following provisioned inputs first:

1. **`record/snapshots/2026-11-14.json` and `record/context.json`:** Application No. `26A686 *** CAPITAL CASE ***`, *Thomas M. Overton, Applicant v. Florida, et al.*, docketed November 14, 2026, linked with *in forma pauperis* certiorari petition No. `26-6154`, arising from the Supreme Court of Florida (`SC2026-1724`, `SC2026-1725`). The single proceeding entry at the arrival cut is: *"Application (26A686) for a stay of execution of sentence of death, submitted to Justice Thomas."* Frozen conditioning signals (`signals_observable: true`, `band: null`): `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`, `vide_links: []`.
2. **`record/documents/documents.json` and `record/documents/application.txt`:** Four-page stay application (`truncated: false`, `empty_text: false`, `ocr_derived: false`) filed by Capital Collateral Regional Counsel — Middle Region. It states that Overton is scheduled for execution on Thursday, November 19, 2026, at 6:00 p.m., asserts generically that Florida's warrant and clemency process violates separation of powers, Due Process, Equal Protection, and the Sixth, Eighth, and Fourteenth Amendments, and cross-references his concurrently filed certiorari petition for substance. Notably, page 2 of `application.txt` retains an unedited template placeholder (*"The Florida Supreme Court denied state court relief as well as Mr. Overton request for stay on [date]."*).

Because `mode` is `forward`, I used unrestricted factual/legal retrieval (strictly excluding any third-party forecasts) to inspect:
- **Live Supreme Court dockets (`26A686` and `26-6154`) on `supremecourt.gov`:** Confirmed that as of November 15, 2026, neither docket has been decided and no subsequent response, referral, or amicus entry has yet posted beyond the November 14 filings.
- **Linked certiorari petition and 60-page appendix in No. `26-6154` (`supremecourt.gov`):** Read the two Questions Presented and the Supreme Court of Florida's November 13, 2026 opinion in *Overton v. State* (`SC2026-1724`) and *Overton v. Secretary, Department of Corrections* (`SC2026-1725`), authored by Justice Tanenbaum and joined by Chief Justice Couriel and Justices Muñiz, Grosshans, Francis, and Barrios, with Justice Labarga concurring in result and **zero dissents** (7–0).
- **Corpus priors (`uv run fedcourts query`) and live dockets for comparable recent capital stay applications:** Retrieved linked docket `26-6154` (`scotus/9026006154`) and recent OT2025–OT2026 resolved substantive capital applications, including three October–November 2026 Florida death-warrant stay applications submitted to Justice Thomas (`26A623` *Jesse Guardado v. Florida*, `26A634` *Jesse Guardado v. Comerford*, and `26A524` *William Reaves v. Florida, et al.*) and `26A661` (*James Dwight Pavatt v. Oklahoma*).
- **CourtListener MCP:** Verified case citations via `analyze_citations` and confirmed prior federal habeas history in *Overton v. Jones*, 155 F. Supp. 3d 1253 (S.D. Fla. 2016), and direct-appeal affirmance in *Overton v. State*, 801 So. 2d 877 (Fla. 2001).

---

## 2. Base-Rate Anchoring (`metrics/statpack.md` and `metrics/statpack.json`)

1. **Scored interim baseline (10-Term pooled finer reading):** Application `26A686` sits in October Term `2026` (prior to OT2027, so the pre-registered 10-Term lookback `2016 <= T < 2026` over `finer_granted` / `finer_resolved` governs). Pooling the ten strictly prior application Terms (`OT2016–OT2025`) from **"The interim docket (applications)"** in `metrics/statpack.md` and `metrics/statpack.json` (`19/218 + 18/189 + 17/124 + 9/103 + 17/107 + 27/133 + 13/119 + 14/113 + 13/124 + 9/107`, with `finer_unread = 0` in all ten Terms; `unparsed` is `0` in OT2018–OT2025, `1` in OT2017, and `15` in OT2016, with OT2020's live-channel total reflecting sparser non-substantive capture) yields **156 granted out of 1,337 substantive resolved applications = 11.67% (11.7%)**, well above the `INTERIM_BASE_RATE_MIN_RESOLVED = 50` floor.
2. **Applicant-class × capital cut (`Substantive applications by applicant class`):** That `11.7%` overall pool is heavily driven by `federal` (`70.8%, 46/65`) and `state` (`47.4%, 37/78`, including `13/20 = 65.0%` where a State applies to *vacate* a lower-court stay of execution) applicants. Under the caption rule (`Thomas M. Overton, Applicant`) and capital docket flag (`bCapitalCase: true`), this cell sits squarely in the **`private` × `capital` cell**:
   - **10-Term `private` × `capital` cell (`OT2016–OT2025`):** **3.5% (`10 / 288`)** (compared against the `private` row margin of `6.1%, 73/1,194` and the `capital` column margin of `9.5%, 30/316`, which mixes prisoner stay requests with federal/state stay-vacatur applications). I lean heavily on the `private` × `capital` cell (`3.5%`, `n = 288`) rather than either margin because prisoner stay-of-execution applications face an asymmetric posture relative to sovereign stay-vacatur applications.
   - **Recent-bench secular shift inside `OT2016–OT2025` (`statpack.json` `applicant_cuts`):** Across the two most recent complete Terms (`OT2024` and `OT2025`), `private` × `capital` applications went **0 for 44 (`0.0%`) in OT2024** and **0 for 44 (`0.0%`) in OT2025** (`0 / 88` combined; `2 / 117 = 1.7%` across `OT2023–OT2025`, vs. `8 / 171 = 4.7%` across `OT2016–OT2022`).
   - **Originating-court cross-check:** On the linked certiorari petition (`26-6154`), petitions from the Supreme Court of Florida in the statpack's originating-court table show **0.0% granted and 0.2% GVR (`n = 612` resolved)**.

---

## 3. Case-Specific Adjustments to `probability = 0.008`

Starting from the `private` × `capital` cell rate of `3.5%` (`10/288` over `OT2016–OT2025`) and the post-2022 bench trend (`0/88` in `OT2024–OT2025`), every case-specific indicator points sharply downward:

1. **Direct recent precedent on identical Florida post-warrant claims:** In its November 13, 2026 unanimous opinion, the Florida Supreme Court rejected Overton's clemency/warrant Due Process claim by citing its decision weeks earlier in *Guardado v. State*, No. SC2026-1605 (Fla. 2026), as well as *Hunt v. State*, 428 So. 3d 43 (Fla. 2025). Corpus and docket records show that Jesse Guardado's ensuing stay-of-execution application to Justice Thomas (`26A623`, decided November 5, 2026 — just ten days ago) was referred to the full Court and denied without any noted dissent, as was `26A524` (*William Reaves v. Florida, et al.*, decided October 20, 2026).
2. **Multiple independent and adequate state-law procedural bars:** Overton's conviction became final in May 2002. The Florida Supreme Court held that his successive Rule 3.851 motion — predicated principally on a 2021 public statement by Governor DeSantis that he would not grant clemency to murderers — was untimely under Fla. R. Crim. P. 3.851(d)(1), barred as successive under Rule 3.851(e)(2), and partially forfeited on appeal; that Florida law recognizes no freestanding postconviction actual-innocence claim (*Herrera v. Collins*, 506 U.S. 390 (1993); *Sweet v. State*, 293 So. 3d 448 (Fla. 2020)); and that his post-warrant Rule 3.852 public-records requests were improper fishing expeditions under state law. Under *Coleman v. Thompson*, 501 U.S. 722, 729 (1991), these independent state procedural bars make No. `26-6154` a fatally flawed vehicle for certiorari.
3. **Foreclosed federal merits under *Woodard*:** Under *Connecticut Board of Pardons v. Dumschat*, 452 U.S. 458 (1981), and *Ohio Adult Parole Authority v. Woodard*, 523 U.S. 272 (1998), executive clemency is discretionary grace subject at most to minimal procedural safeguards. No circuit or state high court has held that a governor's general policy statement regarding murder convictions invalidates state clemency proceedings or creates a federal constitutional right to clemency discovery.
4. **Rushed stay filing:** The four-page stay application adds no tailored vehicle defense or circuit-split authority and leaves an unedited `[date]` placeholder on page 2.

I retain a `0.008` (`0.8%`) residual probability rather than `0.001` only to account for rare unforeseen developments over the five-day warrant window (e.g., an unexpected institutional stay or partial/temporary relief not mooted out before disposition).

---

## 4. Rationale for Escalation Claims, `order-writers`, and `big_case_score`

- **`response-requested-increment = 0.08`:** Importantly, this claim resolves on whether a formal response request is recorded (`response_requested` becoming `true`), *not* whether Florida files a response. Across all four recent denied capital stay applications in our corpus sample (`26A661` *Pavatt*, `26A623` *Guardado*, `26A634` *Guardado*, and `26A524` *Reaves*), respondents filed opposition responses within 1–3 days under standard warrant coordination while **`response_requested` remained `false` in 4 of 4 cases** (`0%`), confirmed verbatim on the `26A623` and `26A524` dockets. I place `0.08` on the small chance that Justice Thomas or the Clerk enters an explicit response-request entry if Florida's filing schedule is not already coordinated.
- **`referral-increment = 0.94`:** Unlike non-capital pro se applications (such as `26A657` and `26A658`, denied single-Justice without referral), active execution-warrant stay applications represented by capital counsel and paired with a pending certiorari petition (`26-6154`) are routinely referred by the Circuit Justice to the full Court so the Court acts simultaneously on both dockets. All six recent substantive capital applications examined in the corpus (`26A661`, `26A623`, `26A634`, `26A524`, `26A428`, `25A1235`) recorded `referred_to_court: true`. I deduct `6%` only for the remote chance of single-Justice action or pre-referral withdrawal/mootness.
- **`amicus-increment = 0.03`:** None of the recent Florida or Oklahoma execution-warrant stay applications (`26A623`, `26A634`, `26A524`, `26A661`) drew an amicus submission, and only five days remain before the scheduled execution. A `3%` allowance covers a low-probability submission by an anti-death-penalty or clemency-focused organization.
- **`order-writers`:** Neither `26A623` (*Guardado*) nor `26A524` (*Reaves*) produced any separate writing or noted dissent. Because `order-writers` requires *authoring* (not merely noting a vote or joining another Justice's dissent), per-Justice probabilities are very low, led by Justice Sotomayor (`0.025`) and Justice Jackson (`0.015`), who author the vast majority of capital denial dissents on the current bench, with `0.001–0.004` across the remaining seven Justices.
- **`big_case_score = 0.22`:** Decoupled from grant odds, a decision on the merits invalidating state clemency procedures where a governor expresses categorical opposition to commuting murder sentences would carry substantial national significance across capital jurisdictions, and any active execution warrant carries life-or-death stakes; however, in its concrete posture — a repetitive, procedurally barred Florida post-warrant template challenge with zero split or amicus engagement — its institutional salience sits in the low-to-moderate tier (`0.22`).

## 5. Key Uncertainties

My primary uncertainty lies on `response-requested-increment` (`0.08`) rather than on disposition (`0.008`): Clerk docketing conventions occasionally record an explicit response deadline on weekend-filed warrant applications even when the State Attorney General already intends to respond, whereas on the disposition itself both historical base rates (`0/88` in `OT2024–OT2025` for `private` × `capital`) and the unanimous procedurally barred decision below leave very little room for a stay.
