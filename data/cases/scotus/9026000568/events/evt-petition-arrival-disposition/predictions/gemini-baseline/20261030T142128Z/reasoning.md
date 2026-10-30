# Predictor Reasoning: *Quinones v. Rodriguez Vazquez*, No. 26-568 (`scotus/9026000568`)

**Event:** `evt-petition-arrival-disposition` (`stage: cert`, `moment: arrival`, `decision_target: disposition`)  
**Snapshot:** `2026-10-30.json` (docketed October 29, 2026; cutoff `2026-10-30`)  
**Salience Band:** `federal` (`sal-v4`)

---

## 1. Base-Rate Anchor (`metrics/statpack.md`)

1. **Overall Modern Discretionary-Cert Base Rate**: Across the live/historical slice of resolved modern discretionary-cert petitions (`metrics/statpack.md`), the denial-reweighted base rate is `denied` 94.8% (`42,577`), `dismissed` 2.0% (`918`), `granted` 1.5% (`692`), and `gvr` 1.3% (`590`) (roughly 2.8% combined grant-family rate). For petitions originating from the Ninth Circuit (`ca9`, `n=5,577` resolved), the denial-reweighted base rate is `denied` 94.8%, `granted` 2.1%, `dismissed` 1.9%, and `gvr` 1.1%.
2. **Scored Segment Base Rate (`band: federal`, `sal-v4`)**: Because this petition is filed by the Solicitor General on behalf of federal immigration officials, it sits in the `federal` salience band. Across the modern discretionary-cert `federal` band (`n=209` resolved in `statpack.md`), the base rate is **`granted` 52.2%, `gvr` 21.5% (73.7% combined grant-family rate), `denied` 23.0%, and `dismissed` 3.3%**. Looking across the strictly prior Terms in the `Segment base rate by salience band (sal-v4)` table (OT2017–OT2025), the `federal` band grant-family rate is:
   - OT2025: 54.2% (`n=24`)
   - OT2024: 60.0% (`n=15`)
   - OT2023: 86.2% (`n=29`)
   - OT2022: 89.5% (`n=19`)
   - OT2021: 75.0% (`n=12`)
   - OT2020: 70.7% (`n=41`)
   - OT2019: 96.2% (`n=26`)
   - OT2018: 47.8% (`n=23`)
   - OT2017: 76.5% (`n=17`)
   Pooling OT2017–OT2025 gives `153 / 206 = 74.3%` grant-family rate for `federal` band petitions.
3. **Merits Disturbed Base Rate for Granted Lead Cases**: Because this petition is explicitly a hold petition tied to *Rhoney v. Barbosa da Cunha*, No. 26-104 (cert. granted Oct. 1, 2026), the relevant baseline for whether *Barbosa da Cunha* will be reversed or vacated—triggering a GVR here—is the Court's merits disturbed rate (`metrics/statpack.md`, *The merits docket*): **70.4%** across `n=565` parsed decisions (OT2025: 73.1%, OT2024: 67.1%, OT2023: 62.5%, OT2022: 69.9%, OT2021: 70.8%).

---

## 2. Case-Specific Signals and Posture Analysis

### A. Explicit Solicitor General Hold Petition for *Rhoney v. Barbosa da Cunha*, No. 26-104
The single most decisive feature of the record is that **this is not a standalone petition for plenary review; it is a Solicitor General hold petition**:
- The sole Question Presented (`questions-presented.txt`) is:
  > *"Whether 8 U.S.C. 1225(b)(2)(A) mandates the detention pending removal proceedings of aliens who, like respondent, are present in the United States without having been admitted."*
- In *Reasons for Granting the Petition* and *Conclusion* (`petition.txt`, p. 11), the Solicitor General states:
  > *"This case presents the question whether 8 U.S.C. 1225(b)(2)(A) mandates the detention of aliens who are present in the United States without having been admitted. This Court granted certiorari in Rhoney v. Barbosa da Cunha, No. 26-104 (Oct. 1, 2026), to consider that question. The Court should therefore hold this petition for a writ of certiorari pending its decision in Barbosa da Cunha and then dispose of the petition as appropriate in light of that decision."*

### B. Procedural Alignment Between *Rodriguez Vazquez* (9th Cir.) and *Barbosa da Cunha* (2d Cir.)
- In *Rodriguez Vazquez v. Bostock*, 183 F.4th 1160 (9th Cir. July 30, 2026), a divided Ninth Circuit panel (Judge Bress writing for the majority, joined by Judge McKeown; Judge Bea dissenting) affirmed the Western District of Washington's grant of partial summary judgment and classwide declaratory relief to the "Bond Denial Class." The Ninth Circuit held that noncitizens who entered the United States without inspection and are later apprehended in the interior are detained under 8 U.S.C. § 1226(a) (which permits release on bond) rather than 8 U.S.C. § 1225(b)(2)(A) (which mandates detention without bond).
- After the panel decision, the Ninth Circuit *sua sponte* ordered briefing on en banc rehearing on September 23, 2026, but following the Supreme Court's October 1, 2026 grant of certiorari in *Rhoney v. Barbosa da Cunha*, No. 26-104 (reviewing *Barbosa da Cunha v. Freden*, 175 F.4th 61 (2d Cir. 2026)), the Ninth Circuit withdrew its en banc briefing order and stayed its mandate pending *Barbosa da Cunha* (`petition.txt`, p. 10).
- In both *Barbosa da Cunha* (2d Cir.) and *Rodriguez Vazquez* (9th Cir.), the court of appeals ruled **against the federal government** on the identical statutory question. And in *Rodriguez Vazquez*, the Solicitor General deliberately elected **not** to raise any separate question concerning 8 U.S.C. § 1252(f)(1) classwide declaratory relief or mootness (`petition.txt`, p. 8 n.2 & p. 11).
- Consequently, the ultimate disposition of *Quinones v. Rodriguez Vazquez* is mechanically linked to the outcome of *Rhoney v. Barbosa da Cunha*:
  - **If the Supreme Court reverses or vacates the Second Circuit in *Barbosa da Cunha*** (holding that § 1225(b)(2)(A) mandates detention of interior-apprehended unadmitted aliens, or vacating on related grounds), the Supreme Court will **GVR (`gvr`)** *Quinones v. Rodriguez Vazquez* in light of *Barbosa da Cunha*. Under the pipeline's schema (`GRANTED_DISPOSITIONS = {granted, granted-in-part, gvr, summary-reversal}`), `gvr` resolves `actual_granted = 1` and `summary-disposition-route = 1`.
  - **If the Supreme Court affirms the Second Circuit in *Barbosa da Cunha*** (holding that § 1226(a), not § 1225(b)(2)(A), governs interior-apprehended unadmitted aliens), the Ninth Circuit's judgment in *Rodriguez Vazquez* is consistent with the Supreme Court's decision, so the Court will **deny (`denied`)** the Solicitor General's held petition (`actual_granted = 0`).

### C. Assessing the Merits Probabilities in *Rhoney v. Barbosa da Cunha*, No. 26-104
To calibrate the probability of `gvr` vs. `denied` in No. 26-568, we evaluate the likelihood that the Government prevails (or obtains vacatur) in *Barbosa da Cunha*:
1. **Strengths of the Government's Position (Fifth & Eighth Circuits; Dissents in Sixth, Ninth, and Eleventh Circuits)**:
   - **Explicit Chapter-Wide Statutory Fiction in § 1225(a)(1)**: Congress in IIRIRA expressly provided that "[a]n alien present in the United States who has not been admitted or who arrives in the United States ... shall be deemed for purposes of this chapter an applicant for admission." 8 U.S.C. § 1225(a)(1). Once an interior EWI noncitizen is deemed an "applicant for admission" as a matter of law, ordinary usage and neighboring subsections (§ 1225(a)(3) "applicants for admission or otherwise seeking admission"; § 1225(a)(4) "An alien applying for admission may ... withdraw the application for admission"; § 1225(a)(5) "purposes and intentions of the applicant in seeking admission") treat "applicant for admission," "applying for admission," and "seeking admission" in § 1225(b)(2)(A) as referring to the same legal status.
   - **IIRIRA's Core Structural Purpose**: A central purpose of IIRIRA in 1996 was to eliminate the pre-1996 "entry" anomaly that rewarded noncitizens who crossed the border illegally without inspection with greater procedural rights than those who presented lawfully at a port of entry. Reading § 1225(b)(2)(A) to resurrect a border-versus-interior divide for bond eligibility reintroduces that disparity.
   - **Supreme Court Track Record on §§ 1225 and 1226**: In *Jennings v. Rodriguez*, 583 U.S. 281 (2018), *Nielsen v. Preap*, 586 U.S. 392 (2019), *DHS v. Thuraissigiam*, 591 U.S. 103 (2020), *Johnson v. Arteaga-Martinez*, 596 U.S. 573 (2022), and *Garland v. Aleman Gonzalez*, 596 U.S. 543 (2022), the Court's conservative majority consistently adhered to strict textual readings of the INA's detention statutes and rejected lower-court efforts to expand bond eligibility.
2. **Strengths of the Respondent's Position (Second, Sixth, Ninth, Tenth, and Eleventh Circuits; Over 90% of District Courts)**:
   - **Textual Surplusage Within § 1225(b)(2)(A)**: Section 1225(b)(2)(A) uses *both* "applicant for admission" and "an alien seeking admission" in the same sentence ("in the case of an alien who is an applicant for admission, if the examining immigration officer determines that an alien seeking admission is not clearly and beyond a doubt entitled to be admitted..."). Because "admission" is defined in § 1101(a)(13)(A) as "the lawful entry of the alien into the United States after inspection and authorization by an immigration officer," reading "seeking admission" to require an active present attempt to enter the country gives independent meaning to every word in § 1225(b)(2)(A), as well as to "examining immigration officer."
   - **Structural Tension with § 1226(c) and the 2025 Laken Riley Act**: Section 1226(c)(1)(A), (D), and (E) carve out specific categories of *inadmissible* aliens from § 1226(a)'s discretionary bond regime and subject them to mandatory detention when they commit enumerated crimes. Most notably, in the Laken Riley Act, Pub. L. No. 119-1, 139 Stat. 3 (Jan. 2025), Congress added 8 U.S.C. § 1226(c)(1)(E) to require mandatory detention of aliens who are inadmissible under § 1182(a)(6)(A) (present without admission or parole) and who are arrested for or charged with theft-related or violent offenses. If *all* aliens inadmissible under § 1182(a)(6)(A) were already subject to mandatory detention without bond under § 1225(b)(2)(A), Congress's 1996 and 2025 enactments in § 1226(c) would be largely redundant as to bond eligibility (affecting only humanitarian parole under § 1182(d)(5)(A) vs. witness-protection release under § 1226(c)(4)), and IIRIRA's 1996 transition rules delaying § 1226(c) due to insufficient bed space would have been inexplicable if § 1225(b)(2)(A) simultaneously mandated immediate detention of millions of non-criminal EWI noncitizens.
   - **Thirty Years of Unbroken Executive Practice and *Jennings* Dicta**: From 1997 (62 Fed. Reg. 10,323) until July 2025, five consecutive presidential administrations interpreted § 1226(a) as governing interior-apprehended EWI noncitizens and § 1225(b)(2)(A) as applying at the border, and *Jennings*, 583 U.S. at 287–89, 303, described the statutory scheme in those exact terms. As the Ninth Circuit majority noted, the Court has recently emphasized statutory context, longstanding practice, and skepticism of newly discovered sweeping powers in aged statutes (*Learning Resources, Inc. v. Trump*, 607 U.S. 229, 245 (2026); *Mullin v. Al Otro Lado*, No. 25-5 (U.S. June 25, 2026)).
3. **Synthesis of Outcome Probabilities**:
   - Starting from the 70.4% merits disturbed rate for granted cases (and ~74% grant-family rate for `federal` band petitions), we adjust **downward** because (a) the 5–2 circuit split against the Government on a massive national detention policy virtually compelled a cert grant in *Barbosa da Cunha* regardless of whether five Justices were already inclined to reverse, and (b) the respondent's structural argument based on § 1226(c) and the 2025 Laken Riley Act, combined with 30 years of uniform post-IIRIRA Executive practice, has strong appeal for textualist Justices (particularly Justices Gorsuch, Barrett, and Chief Justice Roberts, alongside Justices Sotomayor, Kagan, and Jackson).
   - Even with that substantial downward adjustment, the Government remains a slight favorite (~53%–55%) to obtain reversal or vacatur in *Barbosa da Cunha* given the six-Justice conservative majority's jurisprudence on immigration detention and the explicit chapter-wide deeming text of § 1225(a)(1).
   - We therefore assign the following discrete disposition probabilities for *Quinones v. Rodriguez Vazquez*:
     - **`gvr`**: **0.53** (the Court reverses or vacates the Second Circuit in *Barbosa da Cunha* and GVRs *Rodriguez Vazquez* in light of that decision).
     - **`granted`**: **0.02** (small residual probability that the Court grants plenary review, e.g., if a vehicle defect arises in *Barbosa da Cunha* and the Court substitutes or consolidates another pending petition).
     - **`denied`**: **0.43** (the Court affirms the Second Circuit in *Barbosa da Cunha* and denies the Government's hold petition in *Rodriguez Vazquez*).
     - **`dismissed`**: **0.02** (small residual probability of Rule 46 or mootness dismissal).
   - Summing the grant-family dispositions (`gvr` + `granted` + `granted-in-part` + `summary-reversal`) yields **`probability = 0.55`**, **`granted = 1`**, and modal **`predicted_disposition = "gvr"`**.

---

## 3. Mechanical Claims and Distribution Justification

1. **`disposition` (`0.55`)**: Matches `prediction.probability` (`0.53` GVR + `0.02` plenary grant = `0.55`).
2. **`relist-increment` (`0.65`)**: At arrival, `distribution_count` is `0`, so `relist-increment` resolves to `1` if the petition receives at least 2 distributions (`distribution_count >= 2`). Because this is a hold petition for *Rhoney v. Barbosa da Cunha*, it will be distributed once when briefing/waiver completes in late 2026 or early 2027 (where the Court will hold it at conference) and then typically redistributed for the conference following the merits decision in *Barbosa da Cunha* in 2027 when the Court enters its cleanup GVR or denial order. Consistent with corpus patterns on held/GVR petitions (where roughly 60%–70% record `distribution_count >= 2`), we estimate `0.65`.
3. **`cvsg-increment` (`0.001`)**: The Solicitor General is counsel of record for the petitioners (`Federal Parties`). The Court does not invite the Solicitor General to file an amicus brief when the United States is already a party.
4. **`summary-disposition-route` (`0.96`)**: Conditional on the petition resolving in the grant family (`actual_granted == 1`, probability `0.55`), the probability that it resolves by a summary/cert-order disposition (`gvr` or `summary-reversal`) rather than plenary review (`granted`) is `0.53 / 0.55 ≈ 0.964` (`0.96`), because the Solicitor General explicitly asks only for a hold and post-decision disposition in light of *Barbosa da Cunha*.
5. **`dissent-from-denial` (`0.05`)**: Conditional on certiorari being denied (`actual_granted == 0`), which would occur after the Court affirms the Second Circuit in *Barbosa da Cunha*, any dissenting Justices will already have published their merits dissent in *Barbosa da Cunha*. Cleanup denials of held companion petitions are almost always issued as routine unsigned order-list entries without noted dissents, with only a ~5% chance that one or more Justices (e.g., Justice Thomas or Justice Alito) note a dissent or statement on the cleanup order.
6. **`order-writers` (`claim_distributions`)**: Because final disposition of this held petition (whether by GVR or denial) will occur via a routine post-*Barbosa da Cunha* cleanup order, the per-Justice probability of authoring a separate statement or dissent on the order in No. 26-568 is very low across all nine Justices (`0.001` to `0.008`, highest for Justices Thomas and Alito).

---

## 4. Question Presented Topic Classification (`docs/qp-topic.md`)

Under the `qp-topic-v0` / `qp-topic-v1` taxonomy (`docs/qp-topic.md`), the Question Presented ("Whether 8 U.S.C. 1225(b)(2)(A) mandates the detention pending removal proceedings of aliens who, like respondent, are present in the United States without having been admitted") falls squarely under **`immigration`** ("Immigration status, removal, relief, and detention").
