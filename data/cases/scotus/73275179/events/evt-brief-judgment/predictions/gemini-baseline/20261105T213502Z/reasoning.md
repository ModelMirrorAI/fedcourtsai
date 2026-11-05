# Merits Prediction Reasoning: *Cutberto Viramontes, et al. v. Cook County, Illinois, et al.* (No. 25-238)

## 1. Executive Summary & Point Predictions

- **Event**: `evt-brief-judgment` (`stage: merits`, `moment: briefed`, cutoff `2026-10-22`, `mode: forward`)
- **Predicted Judgment**: `reversed` (`granted: 1`, `predicted_disposition: "other"`)
- **P(Disturbed) (`probability` / `judgment-disturbed`)**: `0.88` (comprising `0.80` probability of `reversed` and `0.08` probability of `vacated` or `affirmed-in-part-reversed-in-part`, against `0.12` probability of `affirmed` or undisturbed via DIG/equally divided Court)
- **Predicted Vote Lineup**: **6–3 to reverse**
  - **Majority (6)**: `Roberts`, `Thomas`, `Alito`, `Gorsuch`, `Kavanaugh`, `Barrett`
  - **Dissent (3)**: `Sotomayor`, `Kagan`, `Jackson`
- **Big Case Score**: `0.95` — A watershed Second Amendment challenge to state and municipal bans on AR-15 platform and similar semiautomatic rifles, consolidated with *Grant v. Higgins* (No. 25-566).

---

## 2. Inputs Consulted

This forecast is formed in `forward` mode from the provisioned baseline in `data/cases/scotus/73275179/record/`:
- **Snapshot & Context**: `record/snapshots/2026-10-22.json`, `record/context.json`, and the companion snapshot `record/related/25-566.json` (*Grant v. Higgins*, linked as `Vide` and consolidated with *Viramontes* on May 18, 2026). As required for a merits-stage cell, we ignore the cert-stage salience band (`band: "high"`, `distribution_count: 22`) frozen in `context.json`, since certiorari is already settled.
- **Provisioned Briefs (`record/documents/`)**:
  - `questions-presented.txt`: *"Whether the Second and Fourteenth Amendments guarantee the right to possess AR-15 platform and similar semiautomatic rifles."*
  - `petition.txt`, `brief-in-opposition.txt`, and `cert-reply.txt` (including the Seventh Circuit's June 2, 2025 unpublished order in Appendix A, the Northern District of Illinois's March 1, 2024 summary-judgment opinion in Appendix B, and the Cook County Blair Holt Assault Weapons Ban in Appendix C).
  - `merits-brief-petitioner.txt`: Joint merits brief for the *Viramontes* and *Grant* Petitioners (filed Aug. 28, 2026).
  - `merits-brief-respondent.txt`: Merits brief for the Cook County Respondents (filed Oct. 21, 2026).
  - `merits-amicus-united-states.txt`: Brief for the United States as Amicus Curiae Supporting Petitioners (filed Sept. 2026 by Solicitor General D. John Sauer), urging the Court to reverse the judgments in both consolidated cases.
  - Note: No `decision-below.txt`, `lower-court-docket.txt`, or merits reply briefs were staged in `record/documents/` as of the `2026-10-22` cutoff (the Seventh Circuit's order and district court opinion are reproduced in full in `petition.txt` Appendices A and B). No post-cutoff oral argument transcript exists or was sought.

---

## 3. Statpack Base-Rate Anchoring

### A. Merits Docket Disturbed Rate (`metrics/statpack.md`)
Certiorari in *Viramontes* (No. 25-238) was granted on **May 18, 2026**, which falls in **OT2025** (`grant_term = 2025`). Following the merits anchoring rule (`grant_term - 10 <= T < grant_term`, strictly before `2025`), we pool `disturbed` over `parsed` across the strictly prior grant Terms in the **"The merits docket (granted cases)"** table (**OT2017–OT2024**, the 8 strictly prior grant Terms published in the pack, which carries the `excluded` column):
- **Strictly-Prior Pool (OT2017–OT2024)**:
  - `granted`: **549** (`excluded`: **19** removed by the grant-to-judgment pool guard)
  - `parsed`: **534** (coverage: **534 / 549 = 97.3%**, far above the 30-parsed-judgment minimum floor)
  - `disturbed`: **376** (`239` reversed [44.8%], `125` vacated [23.4%], `12` affirmed in part [2.2%]), vs. `158` undisturbed (`142` affirmed [26.6%], `12` DIG [2.2%], `4` equally divided [0.7%])
  - **Pooled Strictly-Prior Disturbed Base Rate**: **376 / 534 = 70.4%** (and if OT2025's partial `19 / 26` [73.1%, coverage `26 / 53 = 49.1%`, `excluded = 9`] is included across all rendered Terms, `395 / 560 = 70.5%`, coverage `560 / 610 = 91.8%`).

### B. Per-Justice Merits Votes (`metrics/statpack.md`)
Pooling the **"Per-Justice merits votes (complete lineups)"** table across Terms strictly prior to `grant_term = 2025` (**OT2020–OT2024**; **OT2022–OT2024** for Justice Jackson):
- **Kavanaugh**: Sat 238, With judgment **227 (95.4%)**, Disturb **167 of 230 (72.6%)**
- **Roberts**: Sat 238, With judgment **224 (94.1%)**, Disturb **161 of 230 (70.0%)**
- **Barrett**: Sat 232, With judgment **211 (90.9%)**, Disturb **152 of 222 (68.5%)**
- **Alito**: Sat 235, With judgment **188 (80.0%)**, Disturb **139 of 224 (62.1%)**
- **Thomas**: Sat 238, With judgment **187 (78.6%)**, Disturb **140 of 229 (61.1%)**
- **Gorsuch**: Sat 236, With judgment **183 (77.5%)**, Disturb **153 of 224 (68.3%)**
- **Kagan**: Sat 238, With judgment **181 (76.1%)**, Disturb **154 of 225 (68.4%)**
- **Sotomayor**: Sat 238, With judgment **172 (72.3%)**, Disturb **151 of 224 (67.4%)**
- **Jackson**: Sat 147, With judgment **112 (76.2%)**, Disturb **96 of 140 (68.6%)**

---

## 4. Case-Specific Adjustments from the 70.4% Baseline to `0.88`

Starting from the **70.4%** strictly-prior merits disturbed anchor, four case-specific factors justify an upward adjustment of **+17.6 percentage points** to **`0.88`** (`0.80` reversed + `0.08` vacated/reversed-in-part):

1. **The Seventh Circuit's Step-One Holding Was Directly Repudiated in *Wolford v. Lopez* (2026)**:
   In *Viramontes* (Pet. App. 2a–5a), the Seventh Circuit relied on *Bevis v. City of Naperville*, 85 F.4th 1175, 1192–97 (7th Cir. 2023), to hold that plaintiffs bear the threshold burden at *Bruen* step one of proving that AR-15s and similar semiautomatic rifles are "Arms" in common use for individual self-defense rather than military-grade weapons akin to M16s. Last Term in *Wolford v. Lopez*, 609 U.S. 185, 146 S. Ct. 2032, 2043, 2049 (2026), the Supreme Court squarely rejected that approach, holding that step one asks only whether the regulated instruments are "Arms" ("any weapon customarily used for offensive or defensive purposes") and that historical or regulatory limits belong exclusively at step two. Justice Barrett's concurrence specifically admonished lower courts not to "smuggle additional limits, drawn from our regulatory tradition, into the plain-text stage of the inquiry." *Id.* at 2054 n.1. Even Cook County's merits brief (Resp. Br. 21–24) retreats from defending *Bevis*'s claim that semiautomatic rifles are not firearms at step one.

2. **Explicit Prior Statements by Four Sitting Justices on AR-15 Bans**:
   - **Justice Thomas** has repeatedly argued that state and local bans on AR-15s violate *Heller* and *Bruen*: dissenting from the denial of certiorari in *Friedman v. City of Highland Park*, 577 U.S. 1039 (2015) (joined by Justice Scalia), issuing a statement in *Harrel v. Raoul*, 144 S. Ct. 2491 (2024) (calling *Bevis*'s reasoning "nonsensical" and urging review upon final judgment), and dissenting from the denial of certiorari in *Snope v. Brown*, 145 S. Ct. 1534 (2025).
   - **Justices Alito and Gorsuch** noted publicly in *Snope v. Brown*, 145 S. Ct. at 1534, that they would have granted certiorari to review the Fourth Circuit's decision upholding Maryland's AR-15 ban.
   - **Justice Kavanaugh** wrote a landmark dissent in *Heller v. District of Columbia* (*Heller II*), 670 F.3d 1244, 1269–96 (D.C. Cir. 2011), concluding that semiautomatic rifle bans are unconstitutional under *Heller*'s "in common use" standard, and wrote a statement respecting the denial of certiorari in *Snope*, 145 S. Ct. at 1534, stating that *"petitioners have a strong argument that AR-15s are in 'common use' by law-abiding citizens and therefore are protected by the Second Amendment under Heller."*

3. **Unanimous Recognition of AR-15 Popularity in *Smith & Wesson* (2025) and Support of the Solicitor General**:
   - In *Smith & Wesson Brands, Inc. v. Estados Unidos Mexicanos*, 605 U.S. 280, 297 (2025), a unanimous Court stated that AR-15 and AK-47 semiautomatic rifles "are both widely legal and bought by many ordinary consumers" and that "[t]he AR-15 is the most popular rifle in the country."
   - The **United States as amicus curiae** (supporting Petitioners) argues that *Heller*, *McDonald*, *Caetano*, and *Bruen* establish a clear rule: categorical bans on arms that are in common use by law-abiding citizens for lawful purposes are unconstitutional, and historical restrictions on affray, concealed carry of Bowie knives or pistols, trap guns, or automatic machineguns do not justify banning the most popular civilian rifle in America (permitted in 40+ states and owned by 16–26 million Americans). We largely follow the Solicitor General's substantive analysis and disposition recommendation (reversal and remand in both consolidated cases).

4. **Consolidation with *Grant v. Higgins* (No. 25-566) Makes Outright Reversal (`reversed`) Much Likelier Than Narrow Vacatur (`vacated`)**:
   If *Viramontes* had been granted alone, there would be a non-trivial chance the Court might vacate the Seventh Circuit's step-one holding and remand for step-two analysis. However, the Court consolidated *Viramontes* with *Grant v. Higgins* (No. 25-566), where the Second Circuit (*NAGR v. Lamont*, 153 F.4th 213 (2d Cir. 2025)) assumed step one and squarely adjudicated step two on a full summary-judgment record. Because both cases present the identical Question Presented on the ultimate constitutional issue, the Court is overwhelmingly likely to resolve both step one and step two and **reverse** the judgments below (`0.80`), with only a modest (`0.08`) probability of `vacated` or partial reversal (if the Court announces the governing standard and remands to sort through specific statutory features or non-AR-15 models) and `0.12` probability of affirmance / DIG.

---

## 5. Vote Lineup, Authorship, and Uncertainty

- **Votes**: All six Justices in the *Bruen* (2022), *Cargill* (2024), and *Wolford* (2026) majorities (`Roberts`, `Thomas`, `Alito`, `Gorsuch`, `Kavanaugh`, `Barrett`) are expected to vote with the majority to reverse, while `Sotomayor`, `Kagan`, and `Jackson` are expected to dissent.
- **Authorship (`majority-author` & `separate-writers`)**:
  - We assign the highest `majority-author` probabilities to **Chief Justice Roberts (`0.26`)** (who authored *Rahimi* and *Wolford* and often retains landmark Second Amendment cases to preserve clear doctrinal guardrails for machineguns and conversion devices) and **Justice Kavanaugh (`0.25`)** (who authored the *Heller II* dissent and *Snope* statement), followed by **Justice Thomas (`0.18`)** (author of *Bruen* and the *Friedman*/*Harrel*/*Snope* opinions) and **Justice Barrett (`0.10`)**.
  - For `separate-writers`, **Justice Thomas (`0.55`)** is most likely to concur separately (if not assigned the majority), **Justice Sotomayor (`0.55`)** is most likely to author the principal dissent, and **Justices Kavanaugh (`0.42`)**, **Barrett (`0.38`)**, **Jackson (`0.38`)**, **Gorsuch (`0.35`)**, **Alito (`0.32`)**, and **Kagan (`0.30`)** carry substantial separate-writing probabilities given the high salience of the case.
- **Sources of Remaining Uncertainty (`0.12` undisturbed)**:
  - A reader should discount our `0.88` probability only for two possibilities: (1) that Chief Justice Roberts and Justice Barrett (joined by Justice Kavanaugh or Justice Amy Coney Barrett's historical-analogue approach in *Rahimi*) could be persuaded by Cook County's mass-shooting record and Prohibition-era automatic/semiautomatic capacity regulations, though this is unlikely given *Smith & Wesson* and *Snope*; or (2) that the Court could vacate rather than reverse in *Viramontes* due to disputes over how the district court handled Petitioners' summary-judgment exhibits on non-AR-15 firearms (such as Khaya's IMI Galil).
