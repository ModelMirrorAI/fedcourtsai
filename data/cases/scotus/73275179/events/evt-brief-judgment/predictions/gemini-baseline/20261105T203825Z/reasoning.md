# Rationale and Calibration: *Cutberto Viramontes, et al. v. Cook County, Illinois, et al.* (No. 25-238)

## I. Summary of Numbers

- **Binary Prediction (`granted` / `probability` / `judgment-disturbed`)**: `granted: 1`, `probability: 0.91` (`P(disturbed) = 0.91`).
- **Predicted Merits Judgment (`judgment`)**: `reversed` (with `predicted_disposition: "other"` per the merits-stage contract).
- **Predicted Vote Lineup (`votes`)**: 6–3 (`Roberts`, `Thomas`, `Alito`, `Gorsuch`, `Kavanaugh`, `Barrett` in `majority`; `Sotomayor`, `Kagan`, `Jackson` in `dissent`).
- **Big Case Score (`big_case_score`)**: `0.95` — this consolidated case resolves one of the most consequential and closely watched Second Amendment questions since *Heller* and *Bruen*, determining the constitutionality of bans on AR-15 platform and similar semiautomatic rifles enacted by roughly a dozen states and numerous localities.

---

## II. Base-Rate Anchoring (`metrics/statpack.md`)

### 1. Merits Disturbed Rate Anchor (Grant Terms Strictly Prior to OT2025)
In *Viramontes* (No. 25-238), certiorari was granted on **June 30, 2026**, which falls in **October Term 2025** (`context.term: 2025`). Under the merits-stage anchoring rule, we pool `disturbed` over `parsed` across the grant Terms strictly prior to OT2025 within the ten-Term lookback window (`2015 <= T < 2025`) in the **"The merits docket (granted cases)"** table of `metrics/statpack.md`. That section publishes an `excluded (not in granted)` column (confirming the pool guard is active) and carries eight strictly prior grant Terms (`2017` through `2024`):

| Grant Term | Granted | Excluded | Parsed (Coverage) | Affirmed | Reversed | Vacated | In Part | DIG | Eq. Div. | Disturbed | Disturbed Rate |
| --- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| 2024 | 79 | 1 | 77 (97.5%) | 21 | 39 | 13 | 0 | 2 | 2 | 52 | 67.5% |
| 2023 | 56 | 0 | 56 (100.0%) | 17 | 22 | 13 | 0 | 4 | 0 | 35 | 62.5% |
| 2022 | 73 | 1 | 73 (100.0%) | 21 | 24 | 27 | 0 | 1 | 0 | 51 | 69.9% |
| 2021 | 62 | 3 | 62 (100.0%) | 15 | 30 | 8 | 5 | 3 | 1 | 43 | 69.4% |
| 2020 | 80 | 3 | 73 (91.3%) | 13 | 41 | 19 | 0 | 0 | 0 | 60 | 82.2% |
| 2019 | 60 | 2 | 58 (96.7%) | 11 | 33 | 11 | 2 | 1 | 0 | 46 | 79.3% |
| 2018 | 81 | 3 | 78 (96.3%) | 23 | 30 | 20 | 4 | 1 | 0 | 54 | 69.2% |
| 2017 | 58 | 6 | 57 (98.3%) | 21 | 20 | 14 | 1 | 0 | 1 | 35 | 61.4% |
| **Pooled (2017–2024)** | **549** | **19** | **534 (97.3%)** | **142** | **239** | **125** | **12** | **12** | **4** | **376** | **70.4%** |

Across those 534 parsed judgments (well above the 30-judgment minimum floor, with 97.3% parse coverage of the 549 merits-opening grants and 19 cert-order dispositions excluded by the guard), the strictly-prior **merits disturbed base rate is 70.4% (`376 / 534`)**, comprising `reversed` at 44.8% (`239 / 534`), `vacated` at 23.4% (`125 / 534`), and `affirmed-in-part-reversed-in-part` at 2.2% (`12 / 534`), against undisturbed outcomes of `affirmed` at 26.6% (`142 / 534`), `DIG` at 2.2% (`12 / 534`), and `equally divided` at 0.7% (`4 / 534`). (In keeping with the merits-stage instructions, we do not anchor on `context.json`'s `band: "high"`, which is a cert-stage construct.)

### 2. Per-Justice Merits Votes Reference (`metrics/statpack.md`)
Pooling the strictly-prior decision Terms rendered in the **"Per-Justice merits votes (complete lineups)"** section (`OT2020`–`OT2024`, omitting `OT2025` because `OT2025` is this case's grant Term):
- **Roberts**: With judgment `224 / 238` (94.1%); Disturb `161 / 230` (70.0%).
- **Kavanaugh**: With judgment `227 / 238` (95.4%); Disturb `167 / 230` (72.6%).
- **Barrett**: With judgment `211 / 232` (90.9%); Disturb `152 / 222` (68.5%).
- **Gorsuch**: With judgment `183 / 236` (77.5%); Disturb `153 / 224` (68.3%).
- **Alito**: With judgment `188 / 235` (80.0%); Disturb `139 / 224` (62.1%).
- **Thomas**: With judgment `187 / 238` (78.6%); Disturb `140 / 229` (61.1%).
- **Kagan**: With judgment `181 / 238` (76.1%); Disturb `154 / 225` (68.4%).
- **Sotomayor**: With judgment `172 / 238` (72.3%); Disturb `151 / 224` (67.4%).
- **Jackson** (`OT2022`–`OT2024`): With judgment `112 / 147` (76.2%); Disturb `96 / 140` (68.6%).

---

## III. Evidence Read and Case-Specific Adjustments From the 70.4% Baseline

### 1. Provisioned Inputs Consulted
This is a `forward`-mode cell at `moment: briefed` with cutoff `2026-10-22`. From `data/cases/scotus/73275179/record/`, we read:
- `snapshots/2026-10-22.json` and `context.json` (showing the June 30, 2026 grant after 22 distributions, consolidation with No. 25-566 *Grant v. Higgins*, and merits briefing through October 21, 2026);
- `related/related.json` and `related/25-566.json` (the consolidated Second Circuit companion docket, *Grant v. Higgins*);
- All seven provisioned text files in `documents/` listed in `documents.json` (none had `empty_text: true` or `ocr_derived: true`):
  1. `questions-presented.txt` (the single QP on AR-15 platform and similar semiautomatic rifles);
  2. `petition.txt` (including the Seventh Circuit's June 2, 2025 summary affirmance order at Pet. App. 4a–5a and the Northern District of Illinois's March 1, 2024 summary judgment opinion at Pet. App. 6a–25a);
  3. `brief-in-opposition.txt` and `cert-reply.txt`;
  4. `merits-brief-petitioner.txt` (jointly filed by the *Viramontes* and *Grant* petitioners on September 8, 2026);
  5. `merits-amicus-united-states.txt` (brief of the United States as amicus curiae supporting Petitioners, filed September 15, 2026); and
  6. `merits-brief-respondent.txt` (brief of the Cook County Respondents, filed October 15, 2026).

### 2. Why We Adjust Upward From 70.4% to `P(disturbed) = 0.91`
Several strong, convergent signals justify moving substantially above the 70.4% merits disturbed base rate:

1. **Prior On-the-Record Statements by Four Sitting Justices**:
   - In *Snope v. Brown*, 145 S. Ct. 1534 (2025), **Justices Thomas, Alito, and Gorsuch** noted they would have granted certiorari to review the Fourth Circuit's decision upholding Maryland's AR-15 ban, and Justice Thomas's dissent from denial of certiorari (following his earlier writings in *Friedman v. City of Highland Park*, 577 U.S. 1039 (2015), and *Harrel v. Raoul*, 144 S. Ct. 2491 (2024)) laid out the exact merits conclusion that AR-15s are protected "Arms" in common use that cannot be banned under *Heller* and *Bruen*.
   - **Justice Kavanaugh** wrote a separate statement in *Snope*, 145 S. Ct. at 1534, explaining that "millions of Americans own AR-15s," that "Petitioners have a strong argument that AR-15s are in 'common use' by law-abiding citizens and therefore are protected by the Second Amendment under *Heller*," and that the Court "should and presumably will address the AR-15 issue soon, in the next Term or two" once pending cases in the First, Second, Third, Seventh, and Ninth Circuits were decided. Even more tellingly, while on the D.C. Circuit, then-Judge Kavanaugh authored the landmark dissent in *Heller v. District of Columbia* (*Heller II*), 670 F.3d 1244, 1269–96 (D.C. Cir. 2011), concluding that D.C.'s ban on semiautomatic rifles is unconstitutional under *Heller* because semiautomatic rifles fire one bullet per trigger pull, have been in common civilian use for over a century, and are fundamentally distinct from automatic machineguns.

2. **The Court's Immediate Precedent in *Wolford v. Lopez* (June 25, 2026)**:
   - Just five days before granting *Viramontes* and *Grant*, the same six-Justice majority (`Alito`, joined by `Roberts`, `Thomas`, `Gorsuch`, `Kavanaugh`, and `Barrett`, with `Jackson`, `Sotomayor`, and `Kagan` dissenting) decided *Wolford v. Lopez*, 609 U.S. ___, 146 S. Ct. 2039 (June 25, 2026).
   - *Wolford* articulated the three-question plain-text framework at Step One (whether the law applies to "the people," whether it concerns any form of "Arms," i.e., "any weapon customarily used for offensive or defensive purposes," and whether it restricts "keeping" or "bearing" arms). That formulation directly repudiates the Seventh Circuit's holding in *Bevis* / *Viramontes* / *Barnett* that AR-15s are not "Arms" at step one because of their perceived "militaristic" character or that plaintiffs bear a step-one burden to prove common use.
   - Notably, on September 11, 2026, the en banc Third Circuit in *Association of New Jersey Rifle & Pistol Clubs, Inc. v. Attorney General New Jersey*, No. 24-2415 (3d Cir. Sept. 11, 2026), applied *Wolford*, *Bruen*, and *Heller* to strike down New Jersey's ban on the AR-15 and similar semiautomatic rifles.

3. **The Solicitor General's Amicus Brief Supporting Petitioners**:
   - In `merits-amicus-united-states.txt`, the United States strongly supports Petitioners and urges **reversal** of both the Seventh and Second Circuit judgments.
   - Crucially, the Solicitor General's brief provides a clean limiting principle tailored to the institutional concerns of Chief Justice Roberts, Justice Kavanaugh, and Justice Barrett: it explains why semiautomatic rifles (which fire a single round per trigger pull and are owned by over 20 million Americans) are protected arms in common use, while fully automatic machineguns (which fire multiple rounds per trigger pull and have been strictly restricted under federal law since the National Firearms Act of 1934 and 18 U.S.C. § 922(o)) never entered common civilian use and remain validly prohibited.

4. **Consolidation Neutralizing Cook County's Vehicle Objection**:
   - Cook County argues (Resp. Br. 56–62) that the *Viramontes* petitioners waived step-two arguments or failed to build an evidentiary record by stipulating that *Bevis* controlled in the District Court and moving for summary affirmance in the Seventh Circuit.
   - However, Cook County raised this exact objection in its Brief in Opposition (BIO 11–18), and the Court responded by consolidating *Viramontes* with *Grant v. Higgins* (No. 25-566), where the Second Circuit ruled on a fully litigated preliminary-injunction record in *National Ass'n for Gun Rights v. Lamont*, 153 F.4th 213 (2d Cir. 2025). Moreover, the Seventh Circuit itself subsequently reaffirmed *Bevis* on a full bench-trial record in *Barnett v. Raoul* (July 20, 2026), and under *Bruen* and *Wolford* the historical tradition inquiry is a question of law on which the government bears the burden.

### 3. Sources of Uncertainty and Residual Risk (`0.09` Undisturbed; `reversed` vs. `vacated`)
- **Why `P(disturbed)` is `0.91` rather than higher**: We retain a `0.09` probability that the judgment below is left undisturbed (`0.08` `affirmed`, `0.01` `dismissed-as-improvidently-granted`). An affirmance would require at least two of Chief Justice Roberts, Justice Kavanaugh, and Justice Barrett to accept Respondents' step-two argument that AR-15 platform rifles represent a "dramatic technological change" combined with "unprecedented societal concerns" (mass shootings) analogous to 19th-century Bowie-knife laws and 20th-century machinegun restrictions. Given all six conservative Justices' alignment in *Bruen* and *Wolford* and Justice Kavanaugh's *Heller II* dissent and *Snope* statement, that scenario is unlikely but represents the main substantive tail risk.
- **Why `judgment` is `reversed` (`~0.78`) rather than `vacated` (`~0.11`)**: Both Petitioners (Pet. Br. 50) and the United States (U.S. Br. 34) ask the Court to **reverse** the judgments below, just as the Court reversed in *Bruen* and *Wolford*. Because both the Second Circuit in *Grant* and the Seventh Circuit in *Bevis*/*Barnett* already rejected the Second Amendment claim at step two, a vacatur for the lower courts to redo step two is much less likely than an outright reversal holding AR-15 bans unconstitutional, though a modest chance of vacatur remains if the Court announces the governing common-use standard and remands for application to specific statutory feature lists or procedural arguments in *Viramontes*.
