# Merits Rationale (`reasoning.md`): *Kendrick Jarrell Beaird v. United States* (No. 25-5343)

- **Case ID**: `scotus/73277583`
- **Event ID**: `evt-order-judgment` (`stage: merits`, `moment: grant`, `decision_target: judgment`)
- **Mode**: `forward` (`cutoff: 2026-04-21`)
- **Predicted Judgment**: `affirmed` (`granted: 0`, `probability: 0.22`, `predicted_disposition: "other"`)

---

## 1. Record & Retrieval Basis (Moment Disambiguation)

This cell is placed at `moment: grant` (`opened_at: 2026-04-20`, `cutoff: 2026-04-21`) and runs in `forward` mode on October 23, 2026, while the merits decision remains pending.

1. **Provisioned `grant`-moment record (`data/cases/scotus/73277583/record/`)**:
   - **Snapshot**: `2026-04-21.json` (`snapshot_provenance: "truncated"`), reflecting dated proceedings through the April 20, 2026 order granting petitioner's IFP motion and granting certiorari limited to Question 2: *"Whether Stinson v. United States, 508 U.S. 36 (1993), still correctly states the rule for the deference that courts must give the commentary to the Sentencing Guidelines."* (Because the snapshot is a `truncated` reconstruction from a later pull, its undated `Other` counsel block also lists `Anthony J. Dick` of Jones Day as `Court-appointed amicus curiae`.)
   - **Provisioned documents (`record/documents/`)**: Four cert-stage filings were provisioned and read in full (none with `empty_text: true` or `ocr_derived: true`):
     - `questions-presented.txt` (the petition's three questions presented);
     - `petition.txt` (Petition for a Writ of Certiorari filed August 11, 2025 by AFPD Christy Martin and FPD Kevin Joel Page);
     - `brief-in-opposition.txt` (Brief for the United States in Opposition filed January 16, 2026 by Solicitor General D. John Sauer); and
     - `appendix.txt` (containing the Fifth Circuit's unpublished per curiam opinion of May 16, 2025 in No. 24-10763, 2025 WL 1420504, and the August 20, 2024 criminal judgment of the Northern District of Texas in No. 3:23-cr-00028-S).
   - **Provisioned merits briefs / transcript**: None (as expected on a `grant`-moment cell).

2. **Forward-mode retrieval beyond the `grant`-moment baseline**:
   - Because this cell runs in `forward` mode after the case was briefed and argued on October 13, 2026, we retrieved the post-grant merits posture and the full verbatim transcript of the October 13, 2026 oral argument from CourtListener (`audio` ID `106844`, docket `73277583`), along with post-argument coverage.
   - Specifically:
     - On June 30, 2026, the United States filed a *Brief for the United States Supporting Vacatur*, arguing that *Kisor v. Wilkie*, 588 U.S. 558 (2019), modified *Stinson v. United States*, 508 U.S. 36 (1993), and that the Fifth Circuit's judgment should be vacated and remanded for the lower courts to apply *Kisor* in the first instance.
     - Because neither party defended the Fifth Circuit's adherence to unmodified *Stinson* deference, the Supreme Court on May 6, 2026 appointed Anthony J. Dick to brief and argue the case as *amicus curiae* in support of the judgment below.
     - At the October 13, 2026 oral argument, Kevin Joel Page argued for Petitioner Beaird, Deputy Solicitor General Eric J. Feigin argued for the United States supporting vacatur, and Anthony J. Dick argued as Court-appointed amicus curiae supporting affirmance.

---

## 2. Statpack Merits Base-Rate Anchor

Per the merits-stage instructions, we ignore `record/context.json`'s cert-stage salience band (`high`, `sal-v4`) and anchor on **"The merits docket (granted cases)"** section of `metrics/statpack.md`, which publishes an `excluded (not in granted)` column and is therefore quotable.

- **Grant Term**: Certiorari was granted on April 20, 2026, placing this case in **OT2025** (`grant_term = 2025`).
- **Strictly-Prior 10-Term Window (`2015 <= T < 2025`)**: The merits table renders 8 grant Terms in that window carrying parsed judgments (`2017` through `2024`).
- **Pooled Counts and Coverage (`2017–2024`)**:
  - `granted` = `75 + 55 + 74 + 67 + 79 + 56 + 77 + 56` = **539** merits-opening grants (with `34 + 13 + 1 + 1 + 2 + 2 + 0 + 3 = 56` excluded rows removed by the pool guard before the cohort).
  - `parsed` = `73 + 55 + 73 + 65 + 69 + 54 + 75 + 52` = **516** parsed, dated judgments (**95.7%** coverage of `granted`, well above the 30-parsed-judgment floor; the nearest Term, OT2024, stands at `73 / 75 = 97.3%` coverage).
  - `disturbed` (`reversed` + `vacated` + `in part`) = `50 + 34 + 50 + 46 + 57 + 42 + 50 + 31` = **360**.
  - **Baseline P(disturbed)** = `360 / 516` = **69.77%** (**69.8%**, `n = 516`).

---

## 3. Adjustments from the 69.8% Base Rate

### A. Pre-Argument Posture (Why Vehicle & Split Structure Already Tempered the Base Rate)

If evaluated solely on the cert-grant baseline plus the Solicitor General's merits brief supporting vacatur under *Kisor*, one might expect P(disturbed) near or above the **69.8%** base rate. Even before oral argument, however, two features of the record pointed toward a higher-than-usual affirmance probability:
1. **Unfavorable Vehicle for Petitioner Under *Kisor***: As the Brief in Opposition pointed out (BIO 12–13), **every circuit to evaluate USSG § 2K2.1 Application Note 2 under *Kisor***—including the Third Circuit in *United States v. McIntosh*, 124 F.4th 199, 206–11 (3d Cir. 2024), and the Ninth Circuit in *United States v. Trumbull*, 114 F.4th 1114, 1117–21 (9th Cir. 2024)—held that "large capacity magazine" in § 2K2.1(a)(3) is genuinely ambiguous and that Application Note 2 (>15 rounds) warrants deference under *Kisor*. Moreover, the district court stated on the record that it would have imposed the same 72-month sentence regardless of the Guidelines calculation.
2. **Symmetric 6–6 Circuit Split and Limited Grant**: The Court granted certiorari only on Question 2—framed explicitly around whether *Stinson* "still correctly states the rule"—to settle an entrenched 6–6 split led on the *Stinson* side by the Fifth Circuit's en banc decision in *United States v. Vargas*, 74 F.4th 673 (5th Cir. 2023), and appointed Anthony J. Dick to defend the Fifth Circuit's judgment.

### B. Decisive Update from the October 13, 2026 Oral Argument

The verbatim transcript of the October 13, 2026 oral argument provides exceptionally strong evidence that a **7–2 majority** will reject both Petitioner's "no deference" rule and the Solicitor General's proposal to superimpose *Kisor*'s threshold ambiguity test onto *Stinson*, and will **affirm** the Fifth Circuit's judgment:

1. **Chief Justice Roberts**: Questioned why the Court should disturb *Stinson* when post-*Booker* Guidelines are advisory ("why don't they just look at what the Commission meant in the guidelines and move on to the 3553(a) factors? I just think I'm not quite sure that *Stinson* is not a more workable regime"), rejected Petitioner's invocation of *Loper Bright* ("*Loper Bright* concerned executive agencies interpreting statutes instead of courts interpreting them. And I just don't see what *Stinson*, which involves an agency in the judicial branch and issues nonbinding advice, really has much to do with *Loper Bright* at all"), and pressed DSG Feigin on why *Stinson* needed modification when *Stinson* already bars commentary that is inconsistent with the guideline.
2. **Justice Sotomayor**: Strongly defended *Stinson*, noting that Application Note 2 to § 2K2.1 narrows "capable of accepting a large-capacity magazine" by requiring proximity or attachment, and rebuked DSG Feigin for asking the Court to "create chaos in the courts below" and open up "a whole new avenue of legal debate about whether something's ambiguous" across 66,000 annual sentencings over "a sliver of cases."
3. **Justice Jackson**: Emphasized from her Sentencing Commission experience that guidelines text and commentary are "inextricably linked" to establish a uniform national starting point and support the Commission's data-collection mandate, and agreed with Amicus Dick that deference goes only to identifying what the Commission's non-binding recommendation is.
4. **Justice Kavanaugh**: Defended the 30-year *Stinson* + *Williams* + *Booker* + USSG § 1B1.7 framework ("why are we reinventing the wheel when *Stinson* did this 30-some years ago?"), told DSG Feigin that the government's *Kisor* position was "a solution in search of a problem" and that "stability is better served by amicus's position, not yours," and asked Amicus Dick how to craft the majority opinion so that retaining *Stinson* does not undermine *Loper Bright* or *Kisor* for executive agencies.
5. **Justice Kagan**: Despite having authored *Kisor*, pushed back on both Petitioner and the Solicitor General—emphasizing to Petitioner that 28 U.S.C. § 994(a)(2) expressly authorizes policy statements "regarding application of the guidelines," and challenging DSG Feigin that *Stinson* rested primarily on *Williams* rather than *Seminole Rock* and that moving to "Kisor-land" would itself trigger resentencing litigation.
6. **Justice Alito**: Focused on the practical unworkability of district judges defining "large-capacity magazine" without deference to the Commission's policy line-drawing, the disruption to 66,000 annual federal sentencings, and the district court's explicit statement that it would impose the same sentence regardless.
7. **Justice Barrett**: Emphasized USSG § 1B1.7, congressional review, and the reliance of probation officers preparing PSRs, and elicited DSG Feigin's agreement that *Stinson*'s own text already forbids commentary from overriding flatly inconsistent guideline text.
8. **Justices Gorsuch and Thomas**: Justice Gorsuch was the only vocal advocate for overruling *Stinson* under *Loper Bright*, arguing that 28 U.S.C. § 994(a) and 18 U.S.C. § 3553(a) ("consider") contain no express delegation of binding interpretive authority; Justice Thomas asked neutral questions comparing statutory and guideline interpretation and is the likeliest second dissent vote.
9. **The Solicitor General's Explicit Concession**: Twice during oral argument (in exchanges with Justices Sotomayor, Kavanaugh, and Jackson), DSG Feigin stated that if the Court wants to hold that *Kisor* does not apply to the Guidelines and retain *Stinson*, "as a policy matter, I think we'd be very happy with that" and "in many policy respects, we'd prefer that approach."

---

## 4. Residual Uncertainty and Final Calibration

Why do we set `probability` (P(disturbed)) at **0.22** rather than lower?
- First (~17% probability), there remains a live possibility that Chief Justice Roberts or Justice Barrett writes an opinion holding that *Kisor* and *Stinson* are harmonious—stating that *Stinson* incorporates *Kisor*'s rejection of "reflexive deference"—and vacates and remands for the Fifth Circuit to apply that clarified formulation in the first instance (as the United States requested in its merits brief), rather than affirming directly.
- Second (~5% probability), there is a tail possibility that Justice Gorsuch persuades four other conservatives during opinion drafting that *Stinson* cannot be squared with *Loper Bright*, producing a 5–4 reversal or vacatur.

Balancing the **78%** probability of a direct **affirmance** (`affirmed`, `granted: 0`) against the **22%** combined probability of vacatur or reversal yields **`probability: 0.22`**.
