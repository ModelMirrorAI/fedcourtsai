## Operational context

| Field | Value |
|---|---|
| Docket | `26-568` — *Andre Quinones, Acting Director of the Seattle Field Office of U.S. Immigration and Customs Enforcement, et al. v. Ramon Rodriguez Vazquez, Individually and on Behalf of All Others Similarly Situated* |
| Event | `evt-petition-arrival-disposition` (stage: `cert`, moment: `arrival`) |
| Snapshot | `2026-10-30.json` (provenance: `truncated`) |
| Cutoff | `2026-10-30` (`date`, mode: `forward`) |
| Conditioned band | `federal` (`sal-v4`, distribution_count: `0`, cvsg_date: `none`) |
| Documents read | `petition.txt` (`False`), `questions-presented.txt` (`False`) |
| Corpus queries | `6` query invocation(s), `813` GET(s), `212926464` byte(s) |
| CourtListener | `6` call(s) (`3` initial HTTP 429 rate-limit responses, `3` successful opinion searches; `10936657`, `10983473`) |

---

## 1. Executive Summary

We forecast **grant-family disposition (`granted = 1`, `probability = 0.58`)** with modal disposition **`gvr`** (`predicted_disposition = "gvr"`) for the Solicitor General's certiorari petition in *Quinones v. Rodriguez Vazquez*, No. 26-568.

The dispositive structural feature of this cell is that **the Solicitor General explicitly petitions for a hold and follow-on disposition rather than plenary review**. On October 1, 2026, the Supreme Court granted certiorari in *Rhoney v. Barbosa da Cunha*, No. 26-104 (arising from the Second Circuit, *Barbosa da Cunha v. Freden*, 175 F.4th 61 (2d Cir. 2026)), to decide the identical question presented here:

> *"Whether 8 U.S.C. 1225(b)(2)(A) mandates the detention pending removal proceedings of aliens who, like respondent, are present in the United States without having been admitted."*

In the decision below (*Rodriguez Vazquez v. Bostock*, No. 25-6842, decided July 30, 2026), a divided Ninth Circuit panel (Judge Bress, joined by Judge McKeown; Judge Bea dissenting) affirmed summary judgment and declaratory relief in favor of a certified class of unadmitted noncitizens detained at the Northwest ICE Processing Center in Tacoma, Washington. Like the Second Circuit in *Barbosa da Cunha*, the Ninth Circuit held that 8 U.S.C. § 1225(b)(2)(A) applies only to noncitizens seeking entry at the border and that unadmitted noncitizens apprehended in the interior are governed by the discretionary detention and bond-hearing regime of 8 U.S.C. § 1226(a).

In the Petition for a Writ of Certiorari (Pet. 9–10), the Solicitor General states:

> *"This Court granted certiorari in Rhoney v. Barbosa da Cunha, No. 26-104 (Oct. 1, 2026), to consider that question. The Court should therefore hold this petition for a writ of certiorari pending its decision in Barbosa da Cunha and then dispose of the petition as appropriate in light of that decision."*

Because the Ninth Circuit ruled *against* the federal government on the exact statutory question pending in *Barbosa da Cunha*:
- **If the Supreme Court reverses or vacates the Second Circuit in *Barbosa da Cunha*** (holding that § 1225(b)(2)(A) mandates detention of unadmitted interior noncitizens, or vacating on an intermediate ground), the Court will **grant, vacate, and remand (`gvr`)** this held petition in light of *Barbosa da Cunha*. Under the `fedcourtsai` disposition schema, `gvr` belongs to the grant family (`granted = 1`, `summary-disposition-route = 1`).
- **If the Supreme Court affirms the Second Circuit in *Barbosa da Cunha*** (holding that § 1225(b)(2)(A) does not apply to interior detainees and § 1226(a) governs), the Ninth Circuit's judgment below will already align with the Supreme Court's decision, and the Court will **deny (`denied`)** the petition (`granted = 0`).

Accordingly, `P(grant family)` in No. 26-568 is anchored directly to the probability that the federal government prevails (or obtains vacatur) on the merits in *Rhoney v. Barbosa da Cunha*, No. 26-104, which we estimate at **58%** (`0.56` GVR + `0.01` plenary grant + `0.01` summary reversal vs. `0.41` denied + `0.01` dismissed).

---

## 2. Base-Rate Anchoring (`metrics/statpack.md`)

We start from the empirical base rates in `metrics/statpack.md`:

1. **Conditioned Salience Band (`federal`, `sal-v4`)**:
   - In `statpack.md` § 3.2, across the 5-Term lookback window (OT 2020–2024), the `federal` band (`sal-v4`) has a cert grant rate of **13.5%** (139 / 1,032), and across OT 2020–2025 it is **12.5%** (150 / 1,203).
   - At `distribution_count = 0` (`statpack.md` § 3.3), the arrival-moment snapshot reflects the petition the day after docketing (docketed October 29, 2026; snapshot `2026-10-30.json`).
   - Crucially, the `federal` salience band pools *all* paid and IFP-adjusted petitions naming a federal party — the vast majority of which are private petitioners seeking review *against* the United States (where the Solicitor General opposes certiorari). When the **Solicitor General is the petitioner**, historical grant rates are roughly 70%–85% for plenary petitions.

2. **Hold Petitions Pending a Granted Lead Case & Merits Reversal Base Rates**:
   - When the Solicitor General files a hold petition asking the Court to hold a circuit decision pending an already-granted merits case on the identical issue, the petition's ultimate disposition depends on whether the lower court's judgment conflicts with the Supreme Court's eventual merits ruling in the lead case.
   - Here, both the Second Circuit in *Barbosa da Cunha* (No. 26-104) and the Ninth Circuit in *Rodriguez Vazquez* (No. 26-568) ruled against the government. Thus, a reversal or vacatur in *Barbosa da Cunha* translates directly into a **GVR** in *Rodriguez Vazquez*.
   - In `statpack.md` § 5.1, the Supreme Court's overall merits judgment-disturbed (reversal/vacatur) base rate is **71.3%** across OT 2020–2025 (248 / 348; **69.8%** over OT 2020–2024). By originating circuit (`statpack.md` § 5.1), the judgment-disturbed rate is **73.1%** (19 / 26) for the Second Circuit (`ca2`, the court below in *Barbosa da Cunha*) and **77.4%** (41 / 53) for the Ninth Circuit (`ca9`, the court below here).

---

## 3. Case-Specific & Merits Analysis of the Underlying § 1225(b)(2)(A) Dispute

While the ~70%–73% general merits reversal base rate and the Solicitor General's strong track record as petitioner provide the upper anchor, we adjust downward to **58%** after examining the specific statutory arguments in the Ninth Circuit's opinions (`petition.txt`, App. 1a–94a) and the nature of the circuit split:

### A. Why the Grant in *Barbosa da Cunha* Was Driven by an Intractable Circuit Split
In July 2025, DHS/ICE reversed nearly three decades of post-IIRIRA practice and issued guidance (adopted by the BIA in *Matter of Yajure Hurtado*, 29 I. & N. Dec. 216 (BIA 2025)) concluding that noncitizens who entered the United States without inspection and are apprehended in the interior are ineligible for bond hearings under 8 U.S.C. § 1226(a) and must instead be mandatorily detained under 8 U.S.C. § 1225(b)(2)(A). That policy shift sparked thousands of habeas petitions and a deep, rapid circuit split in 2026:
- **For the Government (2 circuits)**: Fifth Circuit (*Buenrostro-Mendez v. Bondi*, 166 F.4th 494 (5th Cir. 2026)) and Eighth Circuit (*Avila v. Bondi*, 170 F.4th 1128 (8th Cir. 2026)).
- **For the Detainees (6 circuits)**: Second Circuit (*Barbosa da Cunha v. Freden*, 175 F.4th 61 (2d Cir. 2026)), Sixth Circuit (*Lopez-Campos v. Raycraft*, 175 F.4th 713 (6th Cir. 2026), over Judge Murphy's dissent), Seventh Circuit (*Castañon-Nava v. DHS*, 175 F.4th 828 (7th Cir. 2026)), Ninth Circuit (*Rodriguez Vazquez v. Bostock*, App. 1a–61a, per Judge Bress over Judge Bea's dissent), Tenth Circuit (*Santillan Quiroz v. Mullin*, 2026 WL 1876709 (10th Cir. June 30, 2026)), and Eleventh Circuit (*Hernandez Alvarez v. Warden*, 175 F.4th 1258 (11th Cir. 2026), over Judge Lagoa's dissent).

Because the circuit split is 6–2 on a major national immigration enforcement policy, the Supreme Court had to grant certiorari in *Barbosa da Cunha* regardless of whether a majority of Justices had pre-committed to reversing the Second Circuit. When certiorari is compelled by an unavoidable circuit conflict on a major federal program, the merits outcome is closer to a competitive statutory contest than in discretionary "error-correction" grants.

### B. Competing Textual and Structural Arguments Before the Supreme Court
- **Strengths of the Government's Position (Supporting Reversal in *Barbosa da Cunha* -> GVR here)**:
  1. **Express Statutory Deeming Clause (`§ 1225(a)(1)`)**: Section 1225(a)(1) commands that "[a]n alien present in the United States who has not been admitted ... shall be deemed for purposes of this chapter an applicant for admission." Section 1225(b)(2)(A) then mandates detention ("shall be detained") "in the case of an alien who is an applicant for admission, if the examining immigration officer determines that an alien seeking admission is not clearly and beyond a doubt entitled to be admitted." As the Fifth and Eighth Circuits and Judges Murphy, Lagoa, and Bea argued, in ordinary English an "applicant for admission" is someone "seeking admission," and neighboring provisions (§ 1225(a)(3)'s "applicants for admission or otherwise seeking admission" and § 1225(a)(5)'s "the applicant in seeking admission") reinforce that equivalence.
  2. **IIRIRA's Structural Overhaul**: Congress enacted § 1225(a)(1) in 1996 specifically to abolish the pre-IIRIRA "entry doctrine" anomaly under which noncitizens who crossed the border unlawfully without inspection enjoyed better procedural treatment than those who presented themselves lawfully at a port of entry.
  3. **Supreme Court Receptiveness in Immigration Detention Cases**: The current Court's conservative majority has consistently favored textualist enforcement readings of INA detention provisions (*Jennings v. Rodriguez*, 583 U.S. 281 (2018); *Nielsen v. Preap*, 586 U.S. 392 (2019); *Johnson v. Arteaga-Martinez*, 596 U.S. 573 (2022)) and recently sided with the government on the textual scope of § 1225 in *Mullin v. Al Otro Lado*, No. 25-5, 2026 WL 1825741 (U.S. June 25, 2026).

- **Strengths of Respondent's Position (Supporting Affirmance in *Barbosa da Cunha* -> Denial here)**:
  1. **Defined Term "Admission" (`§ 1101(a)(13)(A)`) and Surplusage**: "Admission" is statutorily defined as "the lawful entry of the alien into the United States after inspection and authorization by an immigration officer." Reading "an alien seeking admission" examined by an "examining immigration officer" in § 1225(b)(2)(A) to refer to active border/entry inspection gives independent meaning to both "applicant for admission" and "seeking admission," whereas the government's reading renders "seeking admission" redundant.
  2. **Conflict with `§ 1226(a)` and the 2025 Laken Riley Act (`§ 1226(c)(1)(E)`)**: Section 1226(c) carves out specific mandatory-detention exceptions to § 1226(a)'s default bond regime for certain *inadmissible* aliens — most notably § 1226(c)(1)(E), enacted in January 2025 in the Laken Riley Act, which mandates detention for aliens inadmissible under § 1182(a)(6)(A) (present without admission or parole) who are charged with or convicted of theft or burglary offenses. If *all* aliens present without admission were already subject to mandatory detention under § 1225(b)(2)(A), the Laken Riley Act's core provision would be largely superfluous (affecting only the narrow distinction between § 1182(d)(5)(A) parole and § 1226(c)(4) witness-protection release).
  3. **Thirty Years of Unbroken Practice and *Jennings* Dicta**: Across five administrations from 1996 until July 2025 — including explicit Solicitor General representations accepted by the Court in *Jennings*, 583 U.S. at 288–89, 303 — the Executive Branch treated § 1225(b)(2)(A) as governing border arrivals and § 1226(a) as governing interior arrests. As the Court recently emphasized in *Learning Resources, Inc. v. Trump*, 607 U.S. 229, 245, 250 (2026), a three-decade absence of any assertion of such sweeping mandatory authority across administrations weighs heavily against discovering it in an oblique statutory cross-reference, an argument that persuaded prominent conservative appellate judges including Judge Bress below.

Balancing these considerations, we give the federal government a slight edge (**56%–58%**) to prevail (in whole or in part) in *Rhoney v. Barbosa da Cunha*, No. 26-104, given the Court's composition, its recent approach in *Mullin v. Al Otro Lado*, and the textual force of § 1225(a)(1)'s deeming clause.

### C. Vehicle and Mootness Check on No. 26-568
Although named plaintiff Ramon Rodriguez Vazquez received a court-ordered bond hearing, was denied bond, and voluntarily departed the United States (Pet. 6; App. 15a–16a), the Western District of Washington certified a Rule 23(b)(2) "Bond Denial Class" prior to final judgment and entered class-wide declaratory summary judgment (`Rodriguez Vazquez v. Bostock`, App. 15a, 95a–218a). Under *Sosna v. Iowa*, 419 U.S. 393 (1975), and *Gerstein v. Pugh*, 420 U.S. 103 (1975), the certified class's claim remains live despite the named plaintiff's departure. We assign only a **1%** probability to dismissal (`dismissed`).

---

## 4. Breakdown of Disposition Probabilities and Declared Claims

### Disposition Distribution
- **`gvr`: 0.56** — Modal outcome. The Court holds No. 26-568 pending *Rhoney v. Barbosa da Cunha*, No. 26-104, and grants, vacates, and remands after reversing or vacating the Second Circuit in *Barbosa da Cunha*.
- **`granted` (plenary review): 0.01** — Very unlikely because *Barbosa da Cunha* is already granted on the identical question and the Solicitor General requests only a hold.
- **`summary-reversal`: 0.01** — Very unlikely because follow-on held petitions after a plenary merits decision are almost universally resolved via GVR rather than standalone summary reversal.
- **`denied`: 0.41** — If the Supreme Court affirms the Second Circuit in *Barbosa da Cunha*, the Ninth Circuit's decision below will stand and the Court will deny certiorari in No. 26-568.
- **`dismissed`: 0.01** — Small tail probability of Rule 46 dismissal or intervening mootness.

Summing the grant-family dispositions (`gvr` + `granted` + `summary-reversal`) yields **`probability = 0.58`** and **`granted = 1`**, with **`predicted_disposition = "gvr"`**.

### Declared Mechanical Claims (`cert-v3`)
1. **`disposition` (`0.58`)**: Matches the headline grant-family probability (`0.58`).
2. **`relist-increment` (`0.92`)**: At the arrival snapshot (`2026-10-30.json`), `context.distribution_count` is `0`. Under the mechanical resolver (`outcome.signals.distribution_count > context.distribution_count`), any petition that reaches at least one conference distribution resolves to `1`; moreover, because this is a hold petition that will be distributed initially after briefing is completed and then held until *Barbosa da Cunha* is decided (at which point held petitions are redistributed for the post-opinion conference, resulting in `distribution_count >= 2`), the probability of an increment is very high (`0.92`).
3. **`cvsg-increment` (`0.0`)**: The Petitioners are federal officials represented by the Solicitor General (`D. John Sauer`). The Court never issues a CVSG when the United States is already a party, so `cvsg-increment` is `0.0`.
4. **`summary-disposition-route` (`0.98`)**: Conditioned on the petition landing in the grant family (`0.58`), the probability that it is resolved in the cert order itself via GVR (`0.56`) or summary reversal (`0.01`) rather than plenary review (`0.01`) is `0.57 / 0.58 ≈ 0.983` (`0.98`).
5. **`dissent-from-denial` (`0.03`)**: Conditioned on denial (`0.41`), a denial will almost certainly occur as a routine post-decision cleanup order after the Court affirms in *Barbosa da Cunha* (where any dissenting Justices will have already published their views in the plenary opinion). We assign a low `0.03` probability that a Justice notes a separate dissent or statement on the cleanup denial order.

### Distribution Claim (`order-writers`)
Because substantive separate opinions on the § 1225(b)(2)(A) question will be written in the plenary lead case (*Rhoney v. Barbosa da Cunha*, No. 26-104), the per-Justice probability of authoring a separate statement or dissent on the disposition order in No. 26-568 is very small across all nine Justices: slightly elevated for Justices Thomas (`0.010`) and Alito (`0.010`), followed by Sotomayor (`0.006`), Gorsuch (`0.005`), Jackson (`0.005`), Kavanaugh (`0.003`), Barrett (`0.002`), Kagan (`0.002`), and Roberts (`0.002`).

---

## Forecast of the Court's action

The Court will distribute the petition after the response stage and **hold** No. 26-568 pending its merits decision in *Rhoney v. Barbosa da Cunha*, No. 26-104 (cert. granted Oct. 1, 2026), without calling for the views of the Solicitor General (who is already counsel for petitioners). Following the merits decision in *Barbosa da Cunha*, the modal outcome (**56%** unconditional; **98%** conditional on a grant-family disposition) is that the Court will **grant the petition, vacate the Ninth Circuit's judgment, and remand (`gvr`)** for further consideration in light of *Rhoney v. Barbosa da Cunha*, with no separate opinions authored on the disposition order; if the Court instead affirms the Second Circuit in *Barbosa da Cunha*, it will **deny** the petition (**41%**) without noted dissent.
