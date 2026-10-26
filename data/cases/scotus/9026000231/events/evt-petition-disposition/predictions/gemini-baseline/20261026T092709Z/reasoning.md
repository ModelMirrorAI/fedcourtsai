# Predictor Rationale: *Mario Delaine v. United States* (No. 26-231)

## 1. Summary of Forecast

- **Binary Prediction (`granted`)**: `0` (`predicted_disposition`: `"denied"`)
- **`probability` / `disposition` claim (P(any grant))**: `0.11` (11.0%)
- **Declared `cert-v3` Claims**:
  - `disposition`: `0.11`
  - `relist-increment`: `0.98`
  - `cvsg-increment`: `0.001`
  - `summary-disposition-route`: `0.09`
  - `dissent-from-denial`: `0.04`
- **`big_case_score`**: `0.35`

## 2. Inputs Consulted and Conditioning State

This forecast is formed from the provisioned baseline snapshot (`data/cases/scotus/9026000231/record/snapshots/2026-10-26.json`), `record/context.json`, and the provisioned document texts (`questions-presented.txt`, `petition.txt`, and `appendix.txt`, all extracted cleanly with `empty_text: false` and `ocr_derived: false` in `documents.json`), supplemented by the committed `metrics/statpack.md`, corpus queries via `fedcourts query`, and CourtListener MCP verification of the Eleventh Circuit's recent decision in *United States v. Sheely*, No. 24-13967, 2026 WL 2349505 (11th Cir. Aug. 13, 2026), and the Ninth Circuit's en banc decision in *United States v. Gomez*, 165 F.4th 1199 (9th Cir. 2026).

In `record/context.json`, the cell runs in `forward` mode at `stage: cert`, `moment: distribution`, with `salience_version: "sal-v4"`, `band: "baseline"`, `distribution_count: 1`, `cvsg_date: null`, and `term: 2026`.

## 3. Base-Rate Anchoring (`metrics/statpack.md`)

1. **Primary Anchor — `sal-v4` `baseline` Band (`reached` rate)**:
   - Under `metrics/statpack.md` ("Segment base rate by salience band (`sal-v4`)"), pooling the 9 complete Terms strictly preceding OT2026 (OT2017–OT2025), the bracketed `reached` grant-family rate for the `baseline` band (all paid private-petitioner cert petitions that reached `baseline`, including those that subsequently escalated via relists or CVSG) is **5.0%** (`642.2 / 12,883` weighted resolved petitions across OT2017–OT2025: 2025 `3.9% [n=1303]`, 2024 `5.7% [n=1271]`, 2023 `5.9% [n=1312]`, 2022 `5.8% [n=1192]`, 2021 `5.6% [n=1500]`, 2020 `4.5% [n=1739]`, 2019 `4.6% [n=1399]`, 2018 `4.6% [n=1524]`, 2017 `4.7% [n=1643]`).
   - By contrast, the terminal `baseline` rate (petitions that *end* at `distribution_count = 1` without a further distribution) is **1.2%** (`0.8% granted + 0.4% gvr`).
2. **Supporting Cuts (`metrics/statpack.md`)**:
   - **Originating Circuit (`ca6`)**: Modern discretionary-cert petitions from the Sixth Circuit resolve at `1.5% granted + 1.3% gvr = 2.8%` overall (`3.5% granted + 3.0% gvr = 6.5%` unweighted in the live/historical slice).
   - **Relist Count (paid scored segment)**: `relist = 0` resolves at `1.2% granted + 0.5% gvr = 1.7%` (n=10,169), whereas `relist = 1` (`distribution_count = 2`, the `elevated` band) resolves at `8.3% granted + 5.1% gvr = 13.4%` terminal (and across OT2017–OT2025, `elevated`'s bracketed `reached` rate averages **16.9%**, `527.1 / 3,122`).

## 4. Case-Specific Adjustments from the Anchor (`5.0%` → `11.0%`)

### A. Upward Adjustments (`5.0%` → `~18–20%`)
1. **Call for a Response (CFR) Already Issued After Initial Distribution**:
   - The docket snapshot (`2026-10-26.json`) shows a critical procedural sequence: the Solicitor General waived the right to respond on September 18, 2026; the petition was distributed on September 30, 2026 for the October 16, 2026 conference (`distribution_count = 1`); and on **October 14, 2026**, the Court requested a response (originally due November 13, 2026, extended by Justice Kavanaugh on October 26, 2026 to December 14, 2026).
   - Because the Court called for a response *after* the initial distribution, this petition will not terminate in the `relist = 0` (`baseline`) bucket; once the Solicitor General files the Brief in Opposition in December 2026, the petition will necessarily be distributed a second time (`distribution_count >= 2`), moving its trajectory into the `elevated` risk set (~16.9% historical reached rate). Moreover, a CFR following a government waiver confirms that at least one chambers flagged the petition for full briefing rather than letting it die on the waiver dead list.
2. **Elite Supreme Court Counsel and Cert-Stage Amicus Support**:
   - Petitioner is represented by Lisa S. Blatt (Williams & Connolly LLP) alongside Federal Defender Services of Eastern Tennessee, and is supported by a cert-stage amicus brief from the National Association of Criminal Defense Lawyers (NACDL). Paid petitions filed by top-tier Supreme Court specialists with amicus backing and a CFR have a substantially higher grant rate than routine criminal petitions.
3. **Clean Vehicle Preservation on the Single Question Presented**:
   - Below, Delaine challenged all three of his ACCA predicate convictions (2012 Florida aggravated assault, 2009 Florida felony battery, and 2019 Ohio felony domestic violence). The petition strategically drops the other two predicates and presents a single question targeting the 2009 Florida felony battery conviction (Fla. Stat. § 784.041(1)). Because ACCA (18 U.S.C. § 924(e)(1)) requires three qualifying predicates and Delaine had exactly three, invalidating the 2009 Florida felony battery conviction alone would eliminate his 15-year mandatory minimum (and his 188-month Rule 11(c)(1)(C) sentence, which preserved his right to appeal the ACCA enhancement). The issue was squarely pressed and decided in a published opinion by Judge Murphy (*United States v. Delaine*, 171 F.4th 880, 889–92 (6th Cir. 2026)).

### B. Downward Adjustments (`~18–20%` → `11.0%`)
1. **The Claimed Circuit Split Evaporates Under Scrutiny**:
   - Petitioner asserts a "3-3 split" on whether an offense requiring an intentional act, but no mens rea as to the resulting injury, satisfies *Borden v. United States*, 593 U.S. 420 (2021). However, the Solicitor General's forthcoming Brief in Opposition will have a strong response showing that the circuits are **not** divided on statutes like Fla. Stat. § 784.041(1).
   - Under Fla. Stat. § 784.041(1), felony battery requires that a defendant (a) "[a]ctually and intentionally touches or strikes another person against the will of the other," and (b) "[c]auses great bodily harm, permanent disability, or permanent disfigurement." Every circuit to examine Fla. Stat. § 784.041(1) or a materially identical intentional-battery-causing-serious-injury statute agrees it qualifies: the Sixth Circuit here (*Delaine*, 171 F.4th at 889–92), the Eleventh Circuit (*United States v. Vail-Bailon*, 868 F.3d 1293 (11th Cir. 2017) (en banc), and post-*Borden* in *United States v. Sheely*, 2026 WL 2349505 (11th Cir. Aug. 13, 2026)), and the Seventh Circuit (*Douglas v. United States*, 858 F.3d 1069, 1071–72 (7th Cir. 2017)).
   - The cases on the other side of Petitioner's alleged split involved statutes where the underlying conduct did **not** require an intentional touch or strike directed at another person:
     - In *United States v. Gomez*, 165 F.4th 1199 (9th Cir. 2026) (en banc), as Judge Murphy explained below (App. 25a), California assault with a deadly weapon (Cal. Penal Code § 245(a)(1)) can be committed without intending to strike anyone and without even subjective awareness (recklessness) that one's act will apply force to another person. Notably, our corpus query confirms the Supreme Court **denied certiorari in *Gomez v. United States*, No. 25-7193, on May 18, 2026**. Similarly, *United States v. Lopez*, 2026 WL 2165840 (9th Cir. July 28, 2026), addressed federal assault resulting in serious bodily injury (18 U.S.C. § 113(a)(6)), which can be committed via reckless conduct (such as reckless driving).
     - In *United States v. Sjodin*, 161 F.4th 1245 (10th Cir. 2025), California mayhem (Cal. Penal Code § 203) is a general-intent crime that does not require an intentional touch or strike against another person; and in *United States v. Redd*, 85 F.4th 153 (4th Cir. 2023), Maryland first-degree assault covers reckless conduct.
2. **The *Marks* Question Is Non-Outcome-Determinative**:
   - While Petitioner highlights disagreement between the Fourth/Ninth/Tenth Circuits and the Eleventh Circuit over how *Marks v. United States*, 430 U.S. 188 (1977), applies to *Borden*'s 4-1-4 split, both Judge Murphy below (App. 24a) and Judge Rosenbaum concurring in *Sheely*, 2026 WL 2349505, at *7–8, explicitly showed that **the *Marks* issue does not affect the outcome for Fla. Stat. § 784.041(1)**.
   - Under Justice Kagan's four-Justice plurality opinion in *Borden*, the phrase "use of physical force against the person of another" requires a volitional act consciously targeted at another person (`593 U.S. at 431`). Florida felony battery satisfies that targeting requirement because the defendant must "[a]ctually and intentionally touch[] or strike[] another person against the will of the other." And under *Delligatti v. United States*, 604 U.S. 423, 432 (2025), and *Stokeling v. United States*, 586 U.S. 73, 84–85 (2019), an intentional touch or strike that actually causes great bodily harm necessarily involves violent "physical force" capable of causing physical pain or injury under *Johnson v. United States*, 559 U.S. 133, 140 (2010).
   - Meanwhile, under Justice Thomas's view (as Judge Murphy noted at App. 21a–22a, citing *Voisine v. United States*, 579 U.S. 686, 701 n.1 (2016) (Thomas, J., dissenting)), *any* intentional non-consensual touching constitutes an intentional use of physical force designed to cause harm.
3. **Unfavorable Cert/Merits Arithmetic on the Current Court**:
   - The four *Borden* dissenters (Chief Justice Roberts and Justices Alito, Kavanaugh, and Barrett) would include even *reckless* offenses under ACCA's elements clause, and in *Delligatti* (2025) a 7-2 majority held that causing bodily injury or death satisfies the elements clause. Neither wing of the Court is likely to supply four votes to grant review in order to hold that an **intentional battery against another person that causes great bodily harm, permanent disability, or permanent disfigurement** is non-violent under ACCA.

Weighing the positive procedural signals (CFR, Lisa Blatt as counsel of record, NACDL amicus, published opinion discussing *Borden* and *Marks*) against the strong substantive and vehicle counterarguments that the Solicitor General's Brief in Opposition will present, I calibrate `P(grant) = 0.11` (`granted: 0`, `predicted_disposition: "denied"`).

## 5. Rationale for Secondary Claims and Distributions

- **`relist-increment` (`0.98`)**: `context.json` freezes `distribution_count = 1` (the September 30, 2026 distribution for the October 16, 2026 conference). Because the Court requested a response on October 14, 2026 (extended to December 14, 2026), the Clerk will necessarily enter at least one additional `DISTRIBUTED for Conference` entry once the Solicitor General files the Brief in Opposition, unless the petition is dismissed or mooted prior to redistribution (~2%).
- **`cvsg-increment` (`0.001`)**: The United States is the party respondent and has already been ordered to file a Brief in Opposition; an amicus CVSG is virtually impossible.
- **`summary-disposition-route` (`0.09`)**: Conditional on a grant (`P(grant) = 0.11`), plenary review is by far the likeliest path (~91% conditional probability, ~10% unconditional). There is no pending Supreme Court case on point for a hold/GVR, and an SG confession of error is unlikely where both the Sixth and Eleventh Circuits uphold Fla. Stat. § 784.041(1).
- **`dissent-from-denial` (`0.04`) and `order-writers`**: Conditional on denial, there is roughly a 4% probability that a Justice authors a dissent from denial or statement respecting denial—most likely Justice Sotomayor (`0.014`), Justice Jackson (`0.010`), Justice Gorsuch (`0.008`), or Justice Thomas (`0.005`)—given their recurring interest in ACCA, *Borden*, and the application of *Marks* to fractured criminal-law precedents.

## 6. Key Uncertainties

The primary uncertainty is whether at least four Justices view the recurring conceptual question—whether *Borden*'s purposeful/knowing mens rea requirement must attach specifically to the *degree of resulting harm* that supplies *Johnson*-level violent force when the underlying statute requires only an intentional offensive touching—as sufficiently important and cleanly framed by Judge Murphy's opinion to warrant plenary review despite the distinctions in the Ninth and Tenth Circuit assault/mayhem statutes. A secondary uncertainty is whether the Solicitor General's Brief in Opposition (due December 14, 2026) identifies any factual or record complication in Delaine's 2009 Florida state-court conviction documents not discussed by the Sixth Circuit.
