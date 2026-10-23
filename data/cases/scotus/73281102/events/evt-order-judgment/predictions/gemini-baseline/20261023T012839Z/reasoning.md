# Merits Prediction: *William Maxwell v. Albert Thomas, III, Warden* (No. 25-5930)

## 1. Cell Framing, Mode, and Provisioned Inputs

- **Case / Event:** `scotus/73281102` (Supreme Court Docket No. 25-5930, *William Maxwell v. Albert Thomas, III, Warden*, subsequently recaptioned *Maxwell v. Dinis*), `evt-order-judgment` (`stage: merits`, `moment: grant`, `opened_at: 2026-06-01`).
- **Mode and Snapshot Provenance:** We are operating in `forward` mode with `input_snapshot: "2026-06-02.json"` (`snapshot_provenance: "truncated"`, `cutoff: "2026-06-02"`). Because this is a `moment: grant` cell, the provisioned docket snapshot stops on June 2, 2026, the day after certiorari was granted on June 1, 2026, though its counsel table already reflects the appearances of Masha G. Hansford (Davis Polk & Wardwell LLP) for Petitioner, Solicitor General D. John Sauer for Respondent, Brian W. Barnes (Cooper & Kirk, PLLC) as Court-appointed amicus curiae in support of the judgment below, and five amicus groups (Habeas Scholars, NACDL/NAFD, FAMM, Senators Durbin and Booker, and Ranking Member Raskin).
- **Documents Read:** No merits briefs or oral-argument transcript are provisioned in `record/documents/` (as expected for a `moment: grant` cut). We read all five provisioned cert-stage filings in `record/documents/`:
  1. `petition.txt` (pro se petition for certiorari filed Aug. 20, 2025)
  2. `questions-presented.txt`
  3. `appendix.txt` (containing the Fifth Circuit's April 3, 2025 per curiam opinion, 133 F.4th 453; the Eastern District of Texas's October 6, 2023 Memorandum Opinion and Order Adopting R&R; the Magistrate Judge's February 13, 2023 Report and Recommendation; and statutory/regulatory excerpts)
  4. `brief-in-opposition.txt` (Brief for the Respondent in Opposition filed by the Solicitor General on Apr. 16, 2026)
  5. `cert-reply.txt` (Reply Brief for the Petitioner filed by Davis Polk & Wardwell LLP and Paul, Weiss on May 5, 2026)
- **Forward Retrieval Context:** In `forward` mode (the case is pending, with oral argument scheduled for November 2, 2026), we also verified via public docket commentary and CourtListener that the Solicitor General filed a merits brief on August 5, 2026 supporting vacatur of the Fifth Circuit's judgment and was granted divided argument alongside Petitioner, while Brian W. Barnes filed the brief for Court-appointed amicus curiae defending the Fifth Circuit's judgment on September 18, 2026.

---

## 2. Empirical Base Rate Anchor (`metrics/statpack.md`)

Per the merits-stage protocol, we anchor on **"The merits docket (granted cases)"** table in `metrics/statpack.md`, which publishes an `excluded` column (66 summary dispositions removed before the cohort across all Terms).

- **Grant Term Identification:** The event's `opened_at` date is `2026-06-01`, which falls in **October Term 2025** (`grant_term = 2025`). (Note that `stage: merits` does not condition on `context.json`'s cert-stage `band: "high"`).
- **10-Term Preceding Window (`2015 <= T < 2025`):** Across the ten grant Terms strictly preceding OT2025 (comprising the eight populated Terms OT2017–OT2024 in the statpack; OT2015 and OT2016 have no parsed judgments in the table):
  - **Pre-guard grants vs. cohort:** `539` granted cases in the merits cohort, plus `56` excluded cases removed by the grant-to-judgment date guard (`595` pre-guard merits-opening grants).
  - **Parse coverage:** `516` of the `539` granted cases (`95.7%`) have a parsed, dated judgment.
  - **Pooled disturbed rate:** `360 / 516 = 69.8%` (`0.6977`), well above the 30-parsed-judgments minimum floor.
  - **Granular disposition breakdown across OT2017–OT2024 (`n = 516`):**
    - `reversed`: `235 / 516 = 45.5%`
    - `vacated`: `115 / 516 = 22.3%`
    - `affirmed-in-part`: `10 / 516 = 1.9%`
    - `affirmed`: `140 / 516 = 27.1%`
    - `dismissed-improvidently-granted` (`DIG`): `12 / 516 = 2.3%`
    - `equally divided`: `4 / 516 = 0.8%`

Starting from the **69.8%** empirical base rate of disturbance (`granted: true`), we adjust upward to **84.0%** (`0.84`) based on the strong case-specific legal and institutional signals below.

---

## 3. Legal and Institutional Analysis

### A. Question Presented
On June 1, 2026, the Supreme Court granted Maxwell's motion to proceed *in forma pauperis* and granted certiorari limited to the following question:
> *"Whether a claim regarding application of time credits under the First Step Act of 2018, 132 Stat. 5195–5208 (codified in relevant part at 18 U.S.C. §§ 3631–3635), seeking accelerated transfer to a halfway house or home confinement, can be brought in a habeas petition under 28 U.S.C. § 2241."*

The Court declined to grant Petitioner's second question presented regarding whether *Perttu v. Richards*, 605 U.S. 460 (2025), affected the district court's summary-judgment ruling on administrative exhaustion—an issue Petitioner's reply brief (Cert. Reply 2 n.*) expressly agreed did not warrant review by the Supreme Court in the first instance.

### B. Confession of Error by the Solicitor General and Appointment of Amicus
The single strongest case-specific predictor of disturbance here is the position of the United States:
1. In the Brief in Opposition (at 8), the Solicitor General conceded the merits of Question 1, explaining that to the extent the Fifth Circuit held that Petitioner could not challenge the BOP's execution of First Step Act time credits under § 2241 solely because applying those credits toward prerelease custody would not accelerate his ultimate release from his sentence, *"that determination would be inconsistent with language in this Court's opinion in Jones v. Hendrix, 599 U.S. 465 (2023)"* and with the Third Circuit's decision in *Woodall v. Federal Bureau of Prisons*, 432 F.3d 235, 243 (3d Cir. 2005).
2. The Solicitor General opposed certiorari only on two threshold vehicle arguments (administrative exhaustion and supposed intracircuit tension with the unpublished *Cheek* decision). By granting certiorari after requesting a response and relisting the case across the May 21 and May 28, 2026 Conferences (`distribution_count: 3`), the Court rejected those vehicle objections as barriers to resolving the circuit conflict.
3. Because the Solicitor General supports vacatur on the merits, the Court appointed Brian W. Barnes as amicus curiae to defend the Fifth Circuit's judgment. While Court-appointed amici occasionally prevail (e.g., *Jones v. Hendrix* itself, or *Bufkin v. Collins*), when both the criminal/habeas petitioner and the Department of Justice agree that a lower court's jurisdictional/procedural bar to statutory sentence-execution review is erroneous, the Supreme Court disturbs the judgment below in roughly 80–85% of cases.

### C. Doctrinal Merits: Scope of 28 U.S.C. § 2241 and the First Step Act
The Fifth Circuit's two-page per curiam opinion (133 F.4th 453) relied on its "bright-line rule" from *Melot v. Bergami*, 970 F.3d 596, 599 (5th Cir. 2020) (and *Carson v. Johnson*, 112 F.3d 818, 820–821 (5th Cir. 1997)), that *"if a favorable determination of the prisoner's claim would not automatically entitle him to accelerated release, then the proper vehicle is a civil rights suit"* under *Bivens* rather than a habeas petition under 28 U.S.C. § 2241.

That bright-line rule faces formidable textual, precedential, and structural headwinds at the Supreme Court:
1. **Recent Supreme Court Precedent:** In *Jones v. Hendrix*, 599 U.S. 465, 475 (2023), Justice Thomas wrote for the six-Justice conservative majority that § 2241 remains available when a federal prisoner challenges "the legality of his detention" without attacking the validity of his sentence—specifically enumerating claims *"that he is being detained in a place or manner not authorized by the sentence, [or] that he has unlawfully been denied parole or good-time credits."* Likewise, in *Skinner v. Switzer*, 562 U.S. 521, 534 (2011) (quoting *Wilkinson v. Dotson*, 544 U.S. 74, 86 (2005) (Scalia, J., concurring)), the Court recognized that habeas covers relief that would *"terminate custody, accelerate the future date of release from custody, [or] reduce the level of custody."*
2. **Qualitative Difference in Level of Custody:** Transfer from a secure federal prison (FCI Beaumont Low) to community prerelease custody—a residential reentry center (halfway house) or home confinement—fundamentally alters the *place and level of detention*, not merely internal prison conditions like meal service or cell assignments. As the First, Second, and Third Circuits held in *Gonzalez-Fuentes v. Molina*, 607 F.3d 864, 873 (1st Cir. 2010), *Levine v. Apker*, 455 F.3d 71, 77–78 (2d Cir. 2006), and *Woodall v. Federal Bureau of Prisons*, 432 F.3d 235, 242–243 (3d Cir. 2005), challenging the denial of statutory eligibility or credits for community prerelease transfer is a classic challenge to the "execution" of a federal sentence under § 2241.
3. **Mandatory First Step Act Statutory Scheme and the *Bivens* Catch-22:** Under 18 U.S.C. § 3632(d)(4)(C), earned First Step Act time credits *"shall be applied toward time in prerelease custody or supervised release,"* and the BOP Director *"shall transfer eligible prisoners, as determined under section 3624(g), into prerelease custody or supervised release."* The Fifth Circuit's rationale that a federal prisoner must bring a *Bivens* civil-rights suit instead of a § 2241 habeas petition creates an untenable catch-22: *Bivens* is a narrow, disfavored implied damages action against individual officers and does not authorize injunctive relief ordering the BOP to calculate time credits or transfer a prisoner. Thus, Across ideological lines, the Justices are very likely to agree with Petitioner and the Solicitor General that § 2241 is an available vehicle.

### D. Choice of Disposition: `vacated` vs. `reversed`
While both `"vacated"` and `"reversed"` constitute a disturbed judgment (`granted: true`), we must select the single most likely granular disposition and calibrate `disposition_probabilities`:
- **Why `vacated` (0.48) edges out `reversed` (0.34):**
  - In the Eastern District of Texas, the magistrate judge and district court did *not* dismiss Maxwell's petition under *Melot*; instead, they granted summary judgment to the Warden on the ground that Maxwell failed to exhaust his administrative remedies with respect to any First Step Act time-credits claim (Pet. App. 2.2–2.5).
  - On appeal, the Fifth Circuit affirmed *sua sponte* on the threshold *Melot* vehicle ground and explicitly declined to reach exhaustion: *"Accordingly, we need not address whether Maxwell sufficiently exhausted his administrative remedies because, even if he did, § 2241 is not the proper vehicle."* (Pet. App. 1.2). Also, in footnote 1, the Fifth Circuit mistakenly characterized Maxwell's appeal as arising under the First Step Act's Elderly Offender Pilot Program rather than FSA earned time credits.
  - Because the Fifth Circuit bypassed the district court's ground of decision (exhaustion) and relied on a flawed threshold vehicle rule, and because the Solicitor General's merits brief specifically supports **vacatur** so that the Fifth Circuit can address the preserved exhaustion defense on remand (see *Whitman v. Department of Transportation*, 547 U.S. 512, 514–515 (2006)), `"vacated"` ("vacated and remanded") is the modal decretal outcome (`0.48`).
  - However, because the Supreme Court frequently uses `"reversed"` ("reversed and remanded") when squarely overturning a court of appeals' bright-line legal rule even while leaving alternative issues open on remand, `"reversed"` carries substantial probability (`0.34`), with `"affirmed-in-part"` at `0.02`.
- **Paths to an Undisturbed Judgment (`0.16` total):**
  - `"affirmed"` (`0.13`): Court-appointed amicus Brian Barnes argues that the historical core of habeas corpus is restricted to challenges seeking immediate or speedier release from *all* federal custody, and that home confinement and halfway houses remain forms of BOP custody/restraint, making transfers among them challenges to conditions of confinement outside § 2241 (or addressable, if at all, under the APA/federal-question jurisdiction rather than habeas). There is a modest chance (13%) that a majority adopts this strict core-of-habeas rule or affirms on the alternative ground of failure to exhaust.
  - `"dismissed-improvidently-granted"` (`0.03`): There is a small chance (3%) that messy record facts—whether Maxwell's pro se administrative grievances ever actually raised FSA earned time credits, or whether his sentence/release posture moots or clouds the claim—lead the Court to DIG the petition after oral argument.

---

## 4. Summary of Probabilities

| Disposition | Probability | Disturbed (`granted: true`)? |
| --- | --: | :---: |
| `vacated` | 0.48 | Yes |
| `reversed` | 0.34 | Yes |
| `affirmed-in-part` | 0.02 | Yes |
| `affirmed` | 0.13 | No |
| `dismissed-improvidently-granted` | 0.03 | No |
| **Total** | **1.00** | **`probability = 0.84`** |
