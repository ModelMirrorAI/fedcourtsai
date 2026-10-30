# Predictor Rationale: *Nexstar Media Inc. v. National Labor Relations Board* (No. 26-435)

## 1. Summary of Numbers
- **`probability` (`disposition`):** `0.015` (`granted: 0`, `predicted_disposition: "denied"`)
- **`relist-increment`:** `0.06`
- **`cvsg-increment`:** `0.001`
- **`summary-disposition-route`:** `0.65`
- **`dissent-from-denial`:** `0.015`
- **`big_case_score`:** `0.35`

## 2. Base-Rate Anchor (`metrics/statpack.md` and `record/context.json`)
From `record/context.json`, this cell is a `forward` prediction at `moment: distribution` in October Term `2026`, with frozen salience band `band: "baseline"` (`salience_version: "sal-v4"`), `distribution_count: 1`, and `cvsg_date: null`.

In `metrics/statpack.md`, the **"Segment base rate by salience band (`sal-v4`, last 10 Terms)"** table provides the strictly-prior (`2016`–`2025`) bracketed `reached` grant rates for petitions reaching the `baseline` band (the exact population and basis the evaluator scores skill against):
- Across all nine prior Terms with resolved `baseline` cases in the 10-Term window (`2017`–`2025`; `2016` has `n=0`), pooling the bracketed `reached` counts yields approximately `120 / 3,084 = 3.89%`.
- In the two most recent full-capture Terms where the paid scored segment reflects the modern broad denominator rather than small historical subsamples—OT 2024 (`[4.0%] (n=1,355)`) and OT 2025 (`[1.9%] (n=1,354)`)—the pooled `baseline` `reached` rate is `80 / 2,709 = 2.95%`.

Cross-checking the auxiliary cuts in `metrics/statpack.md` for the paid scored segment:
- **Relist count `0 (one conference)`:** `0.3%` granted + `0.2%` GVR = `0.5%` (`n=2,596`), which is the terminal rate for petitions that never relist.
- **CVSG status `no CVSG`:** `3.2%` granted + `0.7%` GVR = `3.9%` (`n=3,037`).
- **Amicus-brief count `0`:** `0.9%` granted + `0.1%` GVR = `1.0%` (`n=1,168`).
- **Originating circuit `ca2`:** `2.9%` granted + `0.6%` GVR = `3.5%` (`n=340`).

I anchor on the strictly-prior `baseline` `reached` base rate of **3.9%** (with the modern OT 2024–2025 `baseline` `reached` rate of **3.0%** in view) and adjust downward to **1.5%** (`0.015`) based on the specific procedural and doctrinal features in the provisioned snapshot (`2026-10-30.json`) and filings (`petition.txt`, `questions-presented.txt`).

## 3. Case-Specific Adjustments from the Record and Legal Context

### A. Procedural Posture: Government Waiver and Zero Amicus Support
The provisioned snapshot (`2026-10-30.json`) shows that the petition was docketed on October 1, 2026, the Solicitor General (representing respondent NLRB) filed a waiver of the right to respond on October 23, 2026, and the petition was distributed on October 28, 2026 for the November 13, 2026 conference. No amicus briefs have been filed. Because the Court does not grant plenary review or issue a contested GVR without first calling for a response (or having a response on file), the immediate question at the November 13 conference is whether any Justice even calls for a response. Most waived petitions with zero amicus briefs are denied at their first conference.

### B. Severe Vehicle Defects in the Decision Below
Reading `petition.txt` (including Appendices A, B, and C) and `questions-presented.txt` reveals three major vehicle problems that weigh heavily against certiorari or a GVR:

1. **Non-precedential Summary Order turning on substantial-evidence review of facts:**
   The Second Circuit's June 30, 2026 decision (*NLRB v. Nexstar Media, Inc.*, No. 24-2818) is an unpublished, non-precedential summary order enforcing an NLRB bargaining order at a single Rochester, New York television station (WROC-TV). Although the summary order's boilerplate standard-of-review paragraph quoted pre-*Loper Bright* Second Circuit decisions (*Bally's Park Place, Inc. v. NLRB*, 646 F.3d 929, 935 (2d Cir. 2011), and *Novelty Crystal Corp. v. NLRB*, 443 F.3d 150, 157 (2d Cir. 2006)) stating that the court gives the Board's legal conclusions "considerable deference," nothing in the panel's decision turned on statutory interpretation. As the panel noted (`petition.txt` App. 10a n.2), Nexstar did not even argue that the Board's long-standing legal definitions of "assign," "responsibly to direct," and "independent judgment" in *Oakwood Healthcare, Inc.*, 348 NLRB 686 (2006), were unlawful under *Loper Bright*. Instead, the dispute was entirely over whether substantial record evidence under 29 U.S.C. § 160(e)–(f) supported the Regional Director's factual findings that WROC-TV's news, digital, and creative services producers functioned collaboratively rather than holding authority to assign or responsibly direct other employees.

2. **The Second Circuit has already adopted *Loper Bright* for NLRB review in a published decision:**
   Petitioner urges either plenary review or a GVR by analogy to *Hospital Menonita de Guayama, Inc. v. NLRB*, 145 S. Ct. 2831 (2025), arguing that the Second Circuit has refused to apply *Loper Bright* to the NLRB. However, a CourtListener check of Second Circuit precedent shows that on September 2, 2026—two months after the unpublished summary order in this case—the Second Circuit issued a published, precedential opinion in *Siren Retail Corp. v. NLRB*, No. 24-3168 (2d Cir. Sept. 2, 2026), explicitly holding that after *Loper Bright*, the Second Circuit no longer defers to the NLRB's interpretations of the NLRA and instead exercises independent judgment. And in *Hospital Menonita de Guayama, Inc. v. NLRB*, 94 F.4th 1 (D.C. Cir. Mar. 1, 2024), the D.C. Circuit had upheld a substantive Board legal doctrine (the successor bar) under *Chevron* three months *before* *Loper Bright* was decided. Here, the summary order was issued two years *after* *Loper Bright*, applied routine substantial-evidence review to workplace facts, and has already been superseded as to standard-of-review language by binding Second Circuit precedent in *Siren Retail*.

3. **No genuine circuit conflict on Question Presented 1:**
   Petitioner's claimed split with *Multimedia KSDK, Inc. v. NLRB*, 303 F.3d 896 (8th Cir. 2002) (en banc), is a fact-bound disagreement comparing evidence at different television stations over two decades apart (and before *Oakwood Healthcare*). The Second Circuit panel expressly distinguished *Multimedia KSDK* on the facts because WROC-TV's producers were not held accountable for other employees' performance (`petition.txt` App. 8a–9a).

## 4. Secondary Claims and Uncertainties
- **`relist-increment` (`0.06`):** There is a small (~6%) chance that a clerk or Justice flags the stray "considerable deference" quote in the Second Circuit's summary order and calls for a response from the Solicitor General to confirm that the outcome did not depend on *Chevron*-style deference, which would produce at least one additional distribution once the BIO arrives.
- **`cvsg-increment` (`0.001`):** Because the NLRB is a federal respondent represented by the Solicitor General, a CVSG is structurally inapplicable.
- **`summary-disposition-route` (`0.65`):** Conditional on a grant, the prior-Term summary-disposition share of grants in `metrics/statpack.md` is roughly 25–36%. Here, conditional on the Court granting a petition arising from an unpublished summary order that recited pre-*Loper Bright* boilerplate, a summary GVR is substantially more plausible than full merits briefing and oral argument, so I set the conditional probability to `0.65`.
- **`dissent-from-denial` (`0.015`) and `order-writers`:** Given the fact-bound posture and the Second Circuit's published decision in *Siren Retail*, a separate statement or dissent from denial is unlikely (`0.015`), with the small probability mass concentrated primarily on Justices Gorsuch (`0.006`), Thomas (`0.005`), and Alito (`0.003`).
- **`big_case_score` (`0.35`):** If the Court were to grant and decide the case on the merits, it would address how *Loper Bright* interacts with substantial-evidence review of NLRB supervisory-status determinations under 29 U.S.C. § 152(11)—a moderately meaningful administrative and labor law issue, though anchored to a routine bargaining-unit dispute.
