# Reasoning: Broadcast Music, Inc. v. North American Concert Promoters Association (`scotus/9026000238`)

**Event:** `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`)  
**Predictor:** `gemini-baseline` (`gemini-4-argon`)  
**Run ID:** `20261029T142045Z`  
**Input Snapshot:** `2026-09-11.json`  

---

## 1. Provisioned Record and Statpack Base-Rate Anchoring

I read the provisioned snapshot (`2026-09-11.json`), `record/context.json`, and all three provisioned document files listed in `record/documents/documents.json` (`questions-presented.txt`, `petition.txt`, and `appendix.txt`, which contains the Second Circuit's May 26, 2026 opinion and Judge Stanton's March 28, 2023 S.D.N.Y. rate-court opinion; note that `appendix.txt` has a pipeline truncation note for the final 829 characters of PDF page 91).

From `record/context.json`:
- `mode`: `"forward"`
- `term`: `2026`
- `band`: `"baseline"` (`salience_version`: `"sal-v4"`)
- `distribution_count`: `1`
- `cvsg_date`: `null`
- `cutoff`: `"2026-09-11"` (`cut_kind`: `"date"`)

### Base-Rate Anchor (`metrics/statpack.md`)
In `metrics/statpack.md`, under **"Segment base rate by salience band (sal-v4)"**, we pool the `baseline` band's bracketed `reached` rate across the 9 rendered Terms strictly preceding OT2026 (OT2017–OT2025):
- OT2025: 4.0% (n=1314) -> ~52.6 grants
- OT2024: 5.9% (n=1274) -> ~75.2 grants
- OT2023: 5.9% (n=1312) -> ~77.4 grants
- OT2022: 5.9% (n=1196) -> ~70.6 grants
- OT2021: 5.7% (n=1500) -> ~85.5 grants
- OT2020: 4.5% (n=1740) -> ~78.3 grants
- OT2019: 4.7% (n=1399) -> ~65.8 grants
- OT2018: 4.8% (n=1529) -> ~73.4 grants
- OT2017: 4.9% (n=1649) -> ~80.8 grants

Across OT2017–OT2025, the pooled `baseline` `[reached]` grant rate is approximately **5.1%** (~659.5 / 12,913 weighted resolved petitions). Looking at other marginal cuts in the statpack for context:
- **Originating court (`ca2`):** In the modern cert petitions table, `ca2` has a resolved base rate of `denied 92.5%, granted 2.7%, dismissed 2.5%, gvr 2.4%` (5.1% grant family over `n=2070` resolved).
- **Amicus count (`0` at disposition):** `denied 95.0%, granted 2.0%, gvr 1.8%` (3.8% grant family over `n=11109` resolved), though as a pending petition at the `response-requested` moment, amicus briefs could still be filed later.

---

## 2. Adjusting for the Moment (`response-requested`) and Case-Specific Factors

### Upward Adjustments (+8.9% from the 5.1% `baseline` `[reached]` anchor, to 0.14)
1. **Call for a Response (CFR) after Waiver:** NACPA waived its right to respond on September 2, 2026, and the petition was distributed on September 9 for the September 28 Long Conference (`distribution_count: 1`). On September 10—the very next day—the Court requested a response. Because petitions in the `baseline` band include thousands of paid petitions where the respondent waives and the Court denies certiorari without ever calling for a response, surviving the initial waiver via a CFR and subsequently being redistributed once the BIO arrives places this petition on the escalator toward the `elevated` band (`[reached]` rate ~16%–19% across prior Terms).
2. **Elite Supreme Court Counsel and Doctrinal Framing:** The petition is filed by Lisa S. Blatt and Williams & Connolly LLP. Counsel cleanly frames the Question Presented around Rule 52(a)(6), *U.S. Bank National Ass'n v. Village at Lakeridge, LLC*, 583 U.S. 387 (2018), and *Bufkin v. Collins*, 604 U.S. 369 (2025), targeting the Second Circuit's categorical statements (relying on *Showtime II*, 912 F.2d 563, 569 n.5 (2d Cir. 1990), and *United States v. ASCAP*, 627 F.3d 64, 76 (2d Cir. 2010)) that whether proposed benchmarks are comparable, how they should be weighed, and what revenue base should be used are "question[s] of law" subject to plenary *de novo* review. Because the Supreme Court has repeatedly granted cases to police the boundary between *de novo* and deferential review of mixed questions (*Lakeridge*, *Monasky v. Taglieri*, *Salve Regina*, *Bufkin*), this framing is substantially stronger than the average paid petition.

### Downward / Moderating Factors (Why P(grant) remains low at 0.14)
1. **Interlocutory Remand Posture:** The Second Circuit did not set a final rate; it vacated the S.D.N.Y.'s rate-court judgment and remanded for recalculation of the rate under the historical ticket-face-value revenue base and for reassessment of the benchmark weights (including whether the GMR-Live Nation and GMR-AEG agreements are appropriate benchmarks). The Supreme Court strongly disfavors interlocutory review where proceedings on remand may narrow or resolve the dispute.
2. **Sui Generis Antitrust Consent-Decree Context vs. General Valuation Split:** While BMI cites cases from the Third, Fourth, Fifth, Seventh, Eighth, Ninth, and Eleventh Circuits applying clear-error review to fair-market valuations and benchmark selection in tax, bankruptcy, eminent domain, and ERISA cases, NACPA's forthcoming brief in opposition will forcefully argue that the split is illusory. Under the BMI and ASCAP antitrust consent decrees, the Southern District of New York is the exclusive rate court in the nation, and appeals go exclusively to the Second Circuit. Thus, no other circuit ever reviews PRO consent-decree rate determinations. Furthermore, the Second Circuit's opinion characterizes its intervention as enforcing legal principles required by the consent decree—such as rejecting benchmarks tainted by supracompetitive market power (GMR's monopoly power over must-have catalogs and ASCAP/BMI supracompetitive leverage) and preventing an unprecedented expansion of the revenue base to box suites and VIP packages where music has no marginal value—rather than re-finding historical facts.
3. **Fact-Bound Record:** Even if the Second Circuit overstated the scope of *de novo* review under *Showtime II*, untangling which portions of its 54-page opinion rested on legal consent-decree constraints versus improper appellate fact-finding across four sets ofPRO licenses (ASCAP, SESAC, GMR, and BMI) and two multi-year rate periods (Retroactive 2014–2018 and Current 2019–2022) makes this a dense, fact-bound vehicle.

Weighing the positive signal of the prompt CFR and Williams & Connolly's strong *Lakeridge* framing against the interlocutory posture and the sui generis Second Circuit consent-decree context, I arrive at **`probability: 0.14`** (`granted: 0`, `predicted_disposition: "denied"`, `confidence: 0.85`).

---

## 3. Rationale for Secondary Claims and Big-Case Score

- **`big_case_score: 0.25`**: While the financial stakes between BMI and the live-concert promotion industry are substantial (over $100 million in royalties across the retroactive and current periods) and the standard of appellate review for fair-market-value benchmarks has doctrinal interest for commercial litigators, the case involves no constitutional issues, major statutory splits of nationwide public salience, or high-profile political controversies.
- **`relist-increment: 0.98`**: On a `response-requested` cell, the petition has only been distributed once (prior to the CFR) and will almost certainly be distributed again once NACPA's response is filed, unless the parties settle and dismiss under Rule 46 (`0.02`).
- **`cvsg-increment: 0.04`**: Because the Question Presented is framed strictly as a Rule 52(a)(6) / *Village at Lakeridge* appellate standard-of-review issue in a private fee dispute rather than a question of antitrust consent-decree interpretation implicating the Department of Justice's enforcement policy, a CVSG is unlikely.
- **`summary-disposition-route: 0.08`**: Conditional on a grant, the Court would almost certainly set the case for plenary briefing and argument rather than issuing a summary reversal or GVR, as *Bufkin* and *Lakeridge* already predated the Second Circuit's ruling.
- **`dissent-from-denial: 0.02` & `order-writers`**: Dissents from denial in interlocutory commercial standard-of-review petitions are rare; small per-Justice probabilities (`0.002`–`0.008`, slightly higher for Thomas and Gorsuch) reflect that low base rate.
