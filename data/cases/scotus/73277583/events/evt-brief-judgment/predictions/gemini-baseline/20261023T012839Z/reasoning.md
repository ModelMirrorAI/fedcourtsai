# Merits Prediction Reasoning — *Kendrick Jarrell Beaird v. United States* (No. 25-5343)

## 1. Executive Summary & Baseline Calibration

- **Event**: `evt-brief-judgment` (`stage: merits`, `moment: briefed`, `mode: forward`)
- **Provisioned Inputs Read**: `record/snapshots/2026-08-26.json`, `record/context.json`, and `record/documents/` (`documents.json`, `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, `appendix.txt`, `merits-brief-petitioner.txt`, `merits-brief-respondent.txt`). Note that although the docket snapshot records the filing of the Court-appointed amicus curiae brief on August 25, 2026, only Petitioner's and Respondent's merits briefs are provisioned in `record/documents/`.
- **Predicted Binary Outcome**: `granted = 1` (judgment below disturbed), `probability = 0.91` (`P(disturbed) = 0.91`)
- **Predicted Merits Judgment**: `vacated` (vacated and remanded), with `predicted_disposition = "other"` per the merits stage convention.

### Base Rates (`metrics/statpack.md` — "The merits docket (granted cases)")
Certiorari in this case was granted on April 20, 2026 (in OT2025; `event.yaml`'s `opened_at` for `evt-brief-judgment` is `2026-08-25`, also within OT2025, and `context.json` records `"term": 2025`). Anchoring on the statpack's **"The merits docket (granted cases)"** table (which publishes the `excluded (not in granted)` guard column removing 66 cert-order dispositions):
- Across the **grant Terms strictly before OT2025** (`2017 <= T < 2025`, the 8 rendered prior Terms in the window), there are **539** granted merits cases (with 56 excluded) and **516** parsed, dated judgments (**coverage: 516 / 539 = 95.7%**). Of those 516 parsed judgments, **360 were disturbed** (235 reversed, 115 vacated, 10 affirmed in part) and **156 were undisturbed** (140 affirmed, 12 DIG, 4 equally divided), yielding a pooled prior-Term **disturbed base rate of 69.8% (`360 / 516`, `n = 516`, coverage `95.7%`)**.
- Including the partially resolved OT2025 grant Term (`24 / 51` parsed, `17 / 24 = 70.8%` disturbed), the full-cohort figure across 2017–2025 is identically **69.8% (`377 / 540`, `n = 540`, coverage `540 / 596 = 90.6%`)**, with **vacated** (`121 / 540 = 22.4%` of all parsed merits decisions, or `32.1%` of disturbed decisions) serving as the standard disposition when the Court corrects a lower court's doctrinal framework and remands for case-specific application.

Starting from the **69.8%** merits disturbance base rate, the posture disclosed by the provisioned merits briefs shifts `P(disturbed)` strongly upward to **0.91** (`judgment: "vacated"`).

---

## 2. Case Posture & Docket Signals (`2026-08-26.json`)

1. **Factual and Procedural Background**:
   Petitioner Kendrick Jarrell Beaird pleaded guilty in the Northern District of Texas to possessing a firearm after a felony conviction under 18 U.S.C. § 922(g)(1), after police found an unloaded Glock 17 pistol equipped with a 17-round magazine in his waistband. At sentencing, the district court applied U.S.S.G. § 2K2.1(a)(3), which sets a base offense level of 22 if the offense involved a "semiautomatic firearm that is capable of accepting a large capacity magazine." The Guideline text does not define "large capacity magazine," while Application Note 2 in the commentary defines it to cover an attached or proximate magazine that can accept "more than 15 rounds of ammunition." Bound by Fifth Circuit precedent, the district court overruled Beaird's objection that Application Note 2 was owed no deference after *Kisor v. Wilkie*, 588 U.S. 558 (2019), calculated an advisory range of 63–78 months (rather than 51–63 months), and imposed a 72-month sentence, adding that it would have imposed the same sentence even if the Guideline range had been calculated differently. The Fifth Circuit affirmed per curiam (`appendix.txt`, 2025 WL 1410410), holding that Beaird's argument was foreclosed by *United States v. Vargas*, 74 F.4th 673 (5th Cir. 2023) (en banc), and *United States v. Martin*, 119 F.4th 410 (5th Cir. 2024).

2. **Limited Certiorari Grant, Government Concession, and Appointment of Amicus Curiae**:
   - In its Brief in Opposition (`brief-in-opposition.txt`, at 9–11), the Solicitor General opposed certiorari on vehicle grounds (pointing to the district court's alternative-sentence statement and arguing that Application Note 2 satisfies *Kisor*), **but agreed with Petitioner that the Fifth Circuit's *Vargas* holding is wrong** and that *Kisor* governs whether Guidelines commentary warrants deference.
   - On April 20, 2026, the Court granted certiorari limited to Question 2 as reformulated by the Court: *"Whether Stinson v. United States, 508 U.S. 36 (1993), still correctly states the rule for the deference that courts must give the commentary to the Sentencing Guidelines."*
   - On May 6, 2026, because the United States agreed that the Fifth Circuit erred and supported vacatur, the Court appointed Anthony J. Dick, Esq., as *amicus curiae* to defend the position that *Stinson* still correctly states the rule.
   - On June 30, 2026, Petitioner filed his merits brief (`merits-brief-petitioner.txt`) and the Solicitor General filed the **Brief for the United States Supporting Vacatur** (`merits-brief-respondent.txt`), both urging the Court to vacate the Fifth Circuit's judgment and remand.

---

## 3. Analysis of the Provisioned Merits Briefs

### A. Unanimous Party Agreement That the Fifth Circuit's Reflexive *Stinson* Rule Cannot Stand
In *United States v. Vargas*, 74 F.4th at 678–683, the en banc Fifth Circuit held that "*Stinson* sets out a deference doctrine distinct from the one refined by *Kisor*" and makes commentary binding "even for 'unambiguous' guidelines" unless it is "plainly erroneous or inconsistent with" the Guideline.

Both `merits-brief-petitioner.txt` and `merits-brief-respondent.txt` demonstrate why that rule will be rejected by the Supreme Court:
- *Stinson* expressly borrowed its standard from *Bowles v. Seminole Rock & Sand Co.*, 325 U.S. 410, 414 (1945), concluding that Guidelines are the equivalent of agency legislative rules and that interpretive commentary "is akin to an agency's interpretation of its own legislative rules." 508 U.S. at 44–45.
- In *Kisor v. Wilkie*, 588 U.S. at 574, the Court held that *Seminole Rock*'s "classic formulation" ("plainly erroneous or inconsistent with the regulation"), if read in a vacuum, suggests "a caricature of the doctrine, in which deference is 'reflexive,'" and reinforced that deference can arise *only* when a regulation remains genuinely ambiguous after exhausting all traditional tools of construction. Justice Kagan's opinion in *Kisor* explicitly cited *Stinson* as one of the decisions applying *Seminole Rock* deference (588 U.S. at 568 n.3).
- Thus, every segment of the Court—both the *Kisor* majority/plurality Justices (Roberts, Sotomayor, Kagan; plus Jackson) and the Justices who sought to overrule *Seminole Rock*/*Auer* in *Kisor* and overruled *Chevron* in *Loper Bright Enterprises v. Raimondo*, 603 U.S. 369 (2024) (Roberts, Thomas, Alito, Gorsuch, Kavanaugh, Barrett)—agrees that *Stinson*'s shorthand does not permit commentary to override unambiguous Guideline text or bypass threshold textual interpretation.

### B. The Doctrinal Divide Between Petitioner and the United States
While both parties ask for vacatur and remand, they disagree on what replaces the Fifth Circuit's reflexive *Stinson* standard:
1. **Petitioner's Position (No Binding Deference / Lenity)**:
   Petitioner (`merits-brief-petitioner.txt`, at 11–45) argues that under the Sentencing Reform Act, 28 U.S.C. § 994(a), (p), and (x) and 18 U.S.C. § 3553(a)(4), only "guidelines" undergo mandatory APA notice-and-comment and the 180-day congressional review period, whereas "commentary" is mentioned only in the excised departure provision of 18 U.S.C. § 3553(b) and can be modified without statutory notice-and-comment or congressional review under Commission Rules 4.1 and 4.3. Invoking *Loper Bright*, 603 U.S. at 391–394, *Rutherford v. United States*, 146 S. Ct. 1320, 1334 (2026), separation of powers, and the rule of lenity, Petitioner urges the Court to hold that courts owe *no* binding deference to Guidelines commentary (or, at minimum, that the rule of lenity resolves any genuine ambiguity during *Kisor* step one).
2. **Respondent's Position (*Kisor*-Cabined *Stinson* Deference)**:
   The Solicitor General (`merits-brief-respondent.txt`, at 11–32) argues that *Stinson*'s analogy to *Seminole Rock* remains valid and that *Kisor*'s framework governs Guidelines commentary. Under *Kisor*, commentary cannot override unambiguous Guideline text, but when a Guideline is genuinely ambiguous and the commentary is reasonable, commentary will routinely satisfy all three *Kisor* character-and-context markers because it is adopted by majority vote of the Commission (Rule 2.2(b)), implicates the Commission's empirical sentencing expertise (28 U.S.C. § 994(o), (w)), and reflects fair and considered judgment (frequently including notice-and-comment and congressional submission, as with the 2006 promulgation of § 2K2.1 Application Note 2).

### C. Why Vacatur and Remand (`judgment: "vacated"`) is the Modal Outcome
Because the Court limited certiorari solely to the doctrinal deference question and neither the Fifth Circuit nor the district court evaluated U.S.S.G. § 2K2.1(a)(3) and Application Note 2 under *Kisor* (or without deference), both Petitioner (Pet. Br. 48) and the United States (Gov't Br. 28–33) agree that the Court should **vacate the judgment below and remand** for the Fifth Circuit to address case-specific issues—including the interpretation of § 2K2.1(a)(3), circuit stare decisis under *Martin*, and harmless error in light of the district court's alternative-sentence statement—in the first instance.

---

## 4. Residual Risks & Calibration of `P(disturbed) = 0.91`

We reserve a **9% probability (`1 - P(disturbed) = 0.09`)** for an undisturbed outcome:
1. **Affirmance on Alternative Grounds (~6%)**: The Court could hold that *Kisor* governs *Stinson* (rejecting the Fifth Circuit's *Vargas* rationale) but proceed to affirm the judgment on the ground that "large capacity magazine" in § 2K2.1(a)(3) is genuinely ambiguous as to the exact numerical threshold and Application Note 2's ">15 rounds" rule warrants *Kisor* deference (the conclusion reached by the Third, Fourth, and Ninth Circuits in *McIntosh*, *Holman*, and *Trumbull*, cited at Gov't Br. 31–32), or because any error was harmless given the district court's explicit statement that it would impose the same 72-month sentence regardless of the Guidelines range. This remains a minority risk because neither party asked the Court to resolve those downstream questions in the first instance.
2. **Dismissal as Improvidently Granted (DIG) (~2%)**: If oral argument focuses heavily on the district court's statement that it would impose the same 72-month sentence regardless of the Guideline calculation, a majority could conclude that the vehicle is unsuitable for resolving the space between *Kisor* deference and no deference and DIG the writ. However, the SG highlighted this exact harmless-error vehicle objection in the BIO (at 12–13) and the Court granted review anyway after 7 distributions.
3. **Adoption of Court-Appointed Amicus's Position (~1%)**: It is highly improbable that five Justices endorse the Fifth Circuit's rule that *Stinson* survives unmodified by *Kisor*.
