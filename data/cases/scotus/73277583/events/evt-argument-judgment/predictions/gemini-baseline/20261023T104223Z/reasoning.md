# Predictor Rationale: *Kendrick Jarrell Beaird v. United States* (No. 25-5343)

## Summary of Forecast

- **Event**: `evt-argument-judgment` (`stage: merits`, `moment: argued`)
- **Predicted Judgment**: `affirmed` (`granted: 0`, `predicted_disposition: "other"`)
- **Probability of Disturbance (`P(disturbed)`)**: **0.28** (corresponding to a **0.72** probability that the Fifth Circuit's judgment is left undisturbed / affirmed).

## Base-Rate Anchor (`metrics/statpack.md`)

Per the merits-stage instructions, I ignore the cert-stage salience band (`band: "high"` in `record/context.json`) and anchor on **"The merits docket (granted cases)"** table in `metrics/statpack.md`, which publishes an `excluded (not in granted)` column and is therefore quotable.

Certiorari in *Beaird* was granted on April 20, 2026, placing this case in **grant Term 2025** (`grant_term = 2025`). Pooling `disturbed` over `parsed` across all grant Terms strictly prior to 2025 within the ten-Term window (`2015 <= T < 2025`, which in the committed statpack spans the 8 rendered grant Terms from OT2017 through OT2024):

| Grant Term | Granted | Excluded | Parsed | Coverage (`parsed/granted`) | Disturbed | Disturbed Rate |
| --- | --: | --: | --: | --: | --: | --: |
| 2024 | 75 | 34 | 73 | 97.3% | 50 | 68.5% |
| 2023 | 55 | 13 | 55 | 100.0% | 34 | 61.8% |
| 2022 | 74 | 1 | 73 | 98.6% | 50 | 68.5% |
| 2021 | 67 | 1 | 65 | 97.0% | 46 | 70.8% |
| 2020 | 79 | 2 | 69 | 87.3% | 57 | 82.6% |
| 2019 | 56 | 2 | 54 | 96.4% | 42 | 77.8% |
| 2018 | 77 | 0 | 75 | 97.4% | 50 | 66.7% |
| 2017 | 56 | 3 | 52 | 92.9% | 31 | 59.6% |
| **Pooled (2017–2024)** | **539** | **56** | **516** | **95.7%** | **360** | **69.8% (n=516)** |

The pooled baseline `P(disturbed)` is **69.8%** (`360 / 516`, well above the 30-parsed-judgment floor, with `516 / 539 = 95.7%` parse coverage). Across those 516 parsed judgments, 140 (`27.1%`) were `affirmed`, 235 (`45.5%`) `reversed`, 115 (`22.3%`) `vacated`, 10 (`1.9%`) `affirmed-in-part-reversed-in-part`, 12 (`2.3%`) `DIG`, and 4 (`0.8%`) `affirmed-by-an-equally-divided-court`.

## Evidence Consulted (`record/documents/` and `record/snapshots/2026-10-14.json`)

This is a `forward` merits cell at `moment: argued`. I read the provisioned snapshot (`2026-10-14.json`) and all nine provisioned document files in `record/documents/` (none had `empty_text: true` or `ocr_derived: true`):
- `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, and `appendix.txt` (containing the Fifth Circuit's May 15, 2025 per curiam affirmance in No. 24-10764 and the Northern District of Texas judgment);
- `merits-brief-petitioner.txt` and `merits-reply-petitioner.txt` (filed by Petitioner Beaird);
- `merits-brief-respondent.txt` and `merits-reply-respondent.txt` (filed by the United States supporting vacatur); and
- `argument-transcript.txt` (the 126-page transcript of the October 13, 2026 oral argument before all nine Justices, featuring Kevin Joel Page for Petitioner, Deputy Solicitor General Eric J. Feigin for the United States supporting vacatur, and Court-appointed *amicus curiae* Anthony J. Dick in support of the judgment below).

## Why `P(disturbed)` Moves from the 69.8% Base Rate Down to 0.28 (`affirmed`)

Before reading the oral argument transcript, the posture of the case—both Petitioner and the Solicitor General supporting vacatur of the Fifth Circuit's judgment, and a 6–6 circuit split on whether *Kisor v. Wilkie*, 588 U.S. 558 (2019), modified *Stinson v. United States*, 508 U.S. 36 (1993)—would ordinarily suggest a high probability of vacatur. However, the October 13, 2026 oral argument transcript provides extraordinarily strong, lopsided evidence that a broad seven-Justice majority rejected **both** Petitioner's "no deference" rule **and** the Solicitor General's "*Kisor* modifies *Stinson*" proposal, and intends to retain *Stinson* intact and affirm the Fifth Circuit:

1. **Why the Court Granted Over the SG's Vehicle Opposition**: Because DOJ changed its litigating position in 2023 to agree with defendants that *Kisor* applies to Guidelines commentary, the Solicitor General was agreeing on the merits with challengers across all circuits while opposing certiorari on vehicle grounds. Granting a case from a *Stinson* circuit (the Fifth Circuit following *United States v. Vargas*, 74 F.4th 673 (5th Cir. 2023) (en banc), and *United States v. Martin*, 119 F.4th 410 (5th Cir. 2024)) and appointing an *amicus* was the only mechanism by which the Court could resolve the 6–6 circuit split in favor of the six circuits (First, Second, Fifth, Seventh, Eighth, and Tenth) that continued to apply *Stinson* unmodified.

2. **Justice-by-Justice Signals at the October 13, 2026 Oral Argument**:
   - **Chief Justice Roberts** stated at the outset of argument that after *United States v. Booker*, 543 U.S. 220 (2005), "the guidelines are advisory. And I'm not sure why we should invite the lower courts to engage in somewhat it strikes me as an academic exercise of interpreting. Why don't they just look at what the Commission meant in the guidelines and move on to the 3553(a) factors? I just think -- I'm not quite sure that, you know, *Stinson* is not a more workable regime." He also rejected Petitioner's reliance on *Loper Bright*, noting that *Stinson* "involves an agency in the judicial branch and issues non-binding advice."
   - **Justice Sotomayor** forcefully opposed both Petitioner and the Solicitor General, asking why *Kisor* upset *Stinson* at all when *Stinson* relied on *Williams v. United States*, 503 U.S. 193 (1992), and U.S.S.G. § 1B1.7, and stating that the half of the circuits that held *Kisor* has no application got it right. When questioning Deputy SG Feigin, she stated she was "at a total loss" as to why the government was "asking us to create chaos in the courts below" across 66,000 sentencings per year for a "sliver of cases" by opening up "a whole new avenue of legal debate about whether something's ambiguous, unambiguous."
   - **Justice Jackson** (a former Vice Chair of the Sentencing Commission) repeatedly emphasized that the Guidelines and commentary are "inextricably linked" as a single mathematical calculation of the Commission's baseline recommendation, that eliminating sentencing disparity requires uniform calculation of that advice, and directly pressed Deputy SG Feigin on why the Court should not simply reject importing *Kisor* into the Guidelines context.
   - **Justice Kavanaugh** emphasized that *Stinson* plus *Booker* plus U.S.S.G. § 1B1.7 have settled this question for over 30 years with annual congressional review. He told Deputy SG Feigin directly that the government's *Kisor* position looked like "a solution in search of a problem" that would lead to "years and years of trying to figure out how much weight you give to particular commentary and different courts going different ways," and that "stability's better served by amicus's position, not yours." During Amicus Dick's argument, Justice Kavanaugh explicitly asked for drafting advice: "I would be concerned if I end up agreeing with your position, I would be concerned about making sure that we do [not do] anything to undermine *Loper Bright* or *Kisor*, and I would want to make that crystal-clear. Your advice on how to do that."
   - **Justice Alito** pressed Petitioner on the unworkability of having hundreds of district judges independently invent definitions of "large capacity magazine" without deferring to what is "essentially a policy call by the Sentencing Commission," noted that commentary goes through notice-and-comment and congressional submission, pointed to the district court's alternative sentence here, and pressed Deputy SG Feigin on the systemic disruption to 66,000 annual sentencings (and potentially 10,000 resentencings from 2025 alone).
   - **Justice Kagan** (the author of *Kisor*) pointed out that 28 U.S.C. § 994(a)(2) broadly authorizes policy statements "regarding application of the guidelines," that the first block of *Stinson* rests on *Williams* rather than *Seminole Rock*, and challenged Deputy SG Feigin that moving to "*Kisor* land, which is a little bit less deferential," would itself generate a wave of resentencing demands.
   - **Justice Barrett** observed that given U.S.S.G. § 1B1.7 and the Commission's notice-and-comment and congressional-submission rules, Petitioner's attack on commentary looked like mere "nomenclature," expressed concern about probation officers preparing Presentence Investigation Reports without authoritative Application Notes, and pressed Deputy SG Feigin on why *Kisor* needed to "modify *Stinson*" at all when *Stinson* itself already forbids following commentary that is flatly inconsistent with the Guideline text.
   - **Justice Gorsuch** was the lone vocal supporter of overruling *Stinson*, arguing that 28 U.S.C. § 994 is silent on commentary, that 18 U.S.C. § 3553(a) only requires courts to "consider" Guidelines, and that *Stinson*'s reliance on statutory silence and ambiguity conflicts with *Loper Bright*. **Justice Thomas** also expressed skepticism of Amicus Dick's "express delegation" framing ("reminds me of my metaphysics class"), suggesting a 7–2 vote split with Justices Gorsuch and Thomas in dissent.

3. **The Solicitor General's Remarkable Concession at the Lectern**: Under questioning from Justices Sotomayor, Kavanaugh, and Jackson, Deputy SG Feigin three times conceded that if the Court preferred to hold that *Kisor* does not apply to the Guidelines and leave *Stinson* intact, "as a policy matter, I think we'd be very happy with that," "in many policy respects, we'd prefer that approach," and "I don't have any real push-back for you." That effectively removed the institutional weight that normally accompanies a government request for vacatur.

## Key Uncertainties and Residual Probability of Disturbance (0.28)

While a question from the bench is not a final vote, seven Justices converging on the same institutional, textual, and *stare decisis* rationale for keeping *Stinson* intact is an unusually clear oral-argument signal. Nonetheless, I retain a **0.28** probability that the judgment below is disturbed (`vacated` ~0.22, `reversed` ~0.06) to account for two residual possibilities:
1. **Narrow *Kisor* / Clarified-*Stinson* Vacatur (~0.22)**: At conference, the Court could decide to write a consensus opinion holding that *Stinson* and *Kisor* are harmonious—specifically, that *Stinson*'s "will bear the construction" / "not inconsistent with" standard already incorporates *Kisor*'s rule that commentary cannot override unambiguous Guideline text—and vacate and remand because the en banc Fifth Circuit in *Vargas* framed *Stinson* and *Kisor* as diverged and suggested commentary might control even unambiguous Guidelines.
2. **Reversal / Vacatur Overruling *Stinson* (~0.06)**: A slim possibility remains that several conservative Justices who joined *Loper Bright* ultimately conclude during opinion drafting that no coherent statutory distinction separates *Stinson* from *Seminole Rock*/*Chevron* and vote to vacate on *de novo* interpretive grounds.
