# Reasoning: *Miguel Angel Delgado, Jr. v. United States* (`scotus/73500250`)

**Event:** `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`)  
**Docket:** No. 25-1347 (Paid petition from the U.S. Court of Appeals for the Fifth Circuit, No. 24-50784)  
**Input Snapshot:** `data/cases/scotus/73500250/record/snapshots/2026-07-27.json` (Cutoff: `2026-07-28`)

---

## 1. Procedural Posture and Conditioning Signals

Petitioner Miguel Angel Delgado, Jr., a former U.S. Customs and Border Protection (CBP) officer, seeks review of a published Fifth Circuit opinion (*United States v. Delgado*, 168 F.4th 752 (5th Cir. Mar. 3, 2026), per Judge Jerry Smith, joined by Chief Judge Elrod and Judge Wilson) affirming his convictions following a three-day bench trial in the Western District of Texas on two counts of deprivation of rights under color of law (18 U.S.C. § 242) and one count of falsifying a record in contemplation of a federal investigation (18 U.S.C. § 1519). Delgado was sentenced to concurrent 24-month prison terms.

From `record/context.json` and the `2026-07-27.json` snapshot:
- **Case Type:** Paid cert petition (`25-1347`), docketed June 3, 2026 (filed May 28, 2026).
- **Respondent:** United States (represented by the Solicitor General).
- **Procedural History at SCOTUS:**
  - June 30, 2026: The Solicitor General waived the right to respond.
  - July 8, 2026: Distributed for the September 28, 2026 (Long) Conference (`distribution_count: 1`).
  - July 27, 2026: **Response Requested** (due August 26, 2026).
- **Salience & Trajectory Signals (`sal-v4`):**
  - `band`: `"baseline"` (private petitioner, `distribution_count = 1` so 0 relists, `cvsg_date = null`).
  - `amicus_briefs`: `null` (0 amicus briefs on the docket as of July 27, 2026).
  - `bCapitalCase`: `false`.

---

## 2. Corpus Base-Rate Anchor

In `metrics/statpack.md`, the segment base rate table (`sal-v4`, *Segment base rate by salience band*) provides the risk-set grant-family rate (`[reached ...]`) for a `baseline`-band paid petition across the prior walked Terms (`OT2017`–`OT2024`, strictly preceding docket Term `2025`; `OT2025` is also shown at `4.0%` [n=1314]):
- Across `OT2017`–`OT2024`, the risk-set (`reached`) grant rate for `baseline` petitions is approximately **5.2%** (`1.8%`–`5.9%` per Term; `OT2024`: 5.9% on n=1274; `OT2023`: 5.9% on n=1312; `OT2022`: 5.9% on n=1196; `OT2021`: 5.7% on n=1500; `OT2020`: 4.5% on n=1740; `OT2019`: 4.7% on n=1399; `OT2018`: 4.8% on n=1529; `OT2017`: 4.9% on n=1649), while the terminal `baseline` grant rate is **~1.2%–1.5%**.
- Overall Fifth Circuit (`ca5`) modern paid/IFP cert petitions resolve at **94.6% denied, 2.1% GVR, 1.7% granted, 1.6% dismissed** (3.8% grant-family rate).
- Here, the Court has issued a **Call for a Response (CFR)** after the Solicitor General initially waived response. Because the bulk of `baseline` petitions in which the respondent waives are denied at the first conference without a CFR, a CFR moves a petition into the subset of `baseline` cases with active interest from at least one Justice (or Clerk's pool recommendation for a response), elevating the conditional probability of a grant or GVR modestly above the raw `~1.3%` terminal baseline toward the `~5–8%` range before accounting for vehicle quality and the forthcoming Brief in Opposition.

---

## 3. Analysis of the Questions Presented and Vehicle Quality

The petition raises four questions challenging the affirmance of Delgado's convictions:

1. **Question 1 — *Barnes v. Felix* and the Fourth Amendment Totality-of-the-Circumstances Inquiry:**
   Petitioner argues that the Fifth Circuit silently reinstated the "moment-of-threat" rule that the Supreme Court unanimously rejected nine months earlier in *Barnes v. Felix*, 605 U.S. 73 (2025). Specifically, Petitioner notes that the Fifth Circuit panel failed to cite *Barnes* and allegedly compartmentalized its analysis—discussing the broader context under the § 242 *mens rea* (willfulness) heading while focusing on the moments when Delgado redirected Espinosa into a door and pressed Estrada into chairs under the Fourth Amendment heading.
   - **Assessment:** This is Petitioner's strongest hook and almost certainly the reason a response was called for (given that *Barnes v. Felix* reversed the Fifth Circuit itself just nine months prior). However, close inspection of Judge Smith's opinion (App. 1a–19a) shows why this is a weak vehicle for either plenary review or a GVR:
     - First, unlike *Barnes* (a civil qualified-immunity/summary-judgment case where the court refused to look at events more than two seconds before a shooting), *Delgado* is a sufficiency-of-the-evidence appeal from a **bench trial** where the district court sat as trier of fact and heard three days of testimony and video evidence.
     - Second, the Fifth Circuit *did* evaluate the pre-seizure history in its Fourth Amendment objective-reasonableness sections (App. 12a–16a). In fact, the pre-seizure history *hurt* Delgado rather than helped him: the expert witness and Delgado's own supervisor testified that Delgado himself "both instigated and escalated" the Espinosa encounter without reason, and in the Estrada encounter, Delgado walked out from behind a secure barrier, unlocked a door, and summoned Estrada into a secure area without patting him down or calling for backup—facts the panel explicitly analyzed under `"c. Objectively Unreasonable"` (App. 15a–16a) to reject Delgado's claim that he reasonably perceived a threat on his life.
     - Once the Solicitor General files a Brief in Opposition pointing out those exact pages of the opinion and explaining that the totality of the circumstances strongly favored the prosecution, the *Barnes* argument will largely evaporate. Still, because the Fifth Circuit omitted any citation to *Barnes* while applying pre-*Barnes* Fifth Circuit precedent (*United States v. Brugman*, 364 F.3d 613 (5th Cir. 2004)), there remains a modest (~4%) chance of a summary GVR in light of *Barnes*.

2. **Question 2 — Willfulness Under 18 U.S.C. § 242 (*Screws v. United States*):**
   Petitioner argues that the circuits are split over whether § 242 willfulness requires subjective awareness of unlawfulness (citing the Second and Sixth Circuits in *Walsh* and *Epley*) or can be inferred from objective unreasonableness, training violations, angry demeanor, and post-incident cover-ups.
   - **Assessment:** This is a classic sufficiency-of-the-evidence challenge dressed up as a circuit split. Because Delgado was convicted at a bench trial and challenges only the sufficiency of the evidence (not jury instructions), any circuit allows a factfinder to infer subjective specific intent circumstantially from blatantly violating use-of-force training, screaming/cursing in a secure facility, and immediately lying to a supervisor and falsifying a report to cover it up. Moreover, the Supreme Court recently denied cert on the same training-violation inference in *United States v. Hill*, 99 F.4th 1289 (11th Cir. 2024), *cert. denied*, 145 S. Ct. 2698 (2025) (cited at App. 10a n.5).

3. **Question 3 — "Bodily Injury" Felony Enhancement Under 18 U.S.C. § 242:**
   Petitioner contends there is a three-way split over whether "bodily injury" under § 242 requires more than *de minimis* injury.
   - **Assessment:** Terrible vehicle. First, does it does not appear Petitioner preserved a statutory interpretation challenge to the definition of "bodily injury" below—the Fifth Circuit noted that "[t]here is undisputed evidence regarding Espinosa's injuries" (head trauma causing lightheadedness, headache, dizziness, ringing in the ears, and confusion after hitting a door) and Estrada's injuries (a bleeding nose laceration after having his face pressed into chairs). Second, a bleeding facial laceration and concussion-like symptoms easily satisfy *any* circuit's definition of bodily injury.

4. **Question 4 — Contemplation of a Federal Investigation Under 18 U.S.C. § 1519:**
   Petitioner argues that his § 1519 conviction depends circularly on the § 242 conviction.
   - **Assessment:** Completely fact-bound sufficiency argument. Delgado was a *federal* CBP officer submitting an official federal report that was reviewed by CBP OPR and DHS OIG.

---

## 4. Synthesis and Probability Calibration

- **Starting Prior:** `~5.2%` risk-set grant-family rate for `baseline` paid cert petitions (`sal-v4` prior Terms `OT2017`–`OT2024`).
- **Upward Adjustments:**
  - The Court called for a response (CFR) on July 27, 2026 after the Solicitor General waived on June 30, 2026. A CFR is a necessary gate for cert/GVR and filters out the ~80–85% of waived petitions that are summarily denied on the first conference list.
  - The Fifth Circuit decided a Fourth Amendment excessive-force appeal nine months after *Barnes v. Felix*, 605 U.S. 73 (2025) (which abrogated the Fifth Circuit's moment-of-threat rule) without citing *Barnes*.
- **Downward Adjustments:**
  - There are zero amicus briefs supporting the petition.
  - The case arises from a **bench trial** where the only preserved appellate issue was sufficiency of the evidence ("any rational trier of fact"), making it a poor vehicle for resolving doctrinal questions on § 242 *mens rea* or "bodily injury" definitions (which normally require contested jury instructions).
  - On the merits of the *Barnes* claim, the Fifth Circuit's opinion explicitly examined the pre-seizure timeline—including Delgado's instigation of the encounters and his decision to leave a protected area, unlock a door, and call Estrada inside without patting him down—which confirmed rather than undermined the excessiveness of the force. Once the Solicitor General highlights this in the BIO, the Court is very likely to deny cert.
- **Final Forecast:**
  - `probability` (P(granted or GVR)): **`0.06`** (6.0%)
  - `granted`: **`0`**
  - `predicted_disposition`: **`"denied"`**
  - **Declared Cert Claims (`cert-v3`):**
    - `disposition`: `0.06` (matches top-level `probability`: ~4% GVR in light of *Barnes v. Felix* + ~2% plenary review, vs. ~93.5% denied and ~0.5% dismissed).
    - `relist-increment`: `0.96` (at `distribution_count = 1`, the petition was distributed on July 8, 2026 for the 9/28/2026 conference before the July 27 CFR; once the SG files its response, the petition will be redistributed for a subsequent conference, raising `distribution_count` to at least 2 unless withdrawn/dismissed beforehand).
    - `cvsg-increment`: `0.0` (the United States is a party respondent).
    - `summary-disposition-route`: `0.67` (conditional on a grant, a summary GVR in light of *Barnes v. Felix* [~4% unconditional] is roughly twice as likely as plenary review [~2% unconditional]).
    - `dissent-from-denial`: `0.03` (conditional on denial, a separate dissent or statement respecting denial is unlikely given the bench-trial sufficiency posture, with small per-Justice writing probabilities in `order-writers` led by Gorsuch at `0.012`, Thomas at `0.010`, and Sotomayor at `0.010`).
