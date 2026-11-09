# Certiorari Prediction: *Derick Irisha Brown v. United States* (No. 25-1342)

- **Case ID**: `scotus/73500244`
- **Event**: `evt-petition-disposition` (certiorari disposition at distribution)
- **Predicted Disposition**: `denied` (`granted: false`)
- **Probability of Grant**: `0.12` (12%)

---

## 1. Case Overview and Question Presented

Petitioner Derick Irisha Brown was convicted in the Northern District of Alabama of kidnapping resulting in death and conspiracy to kidnap under the Federal Kidnapping Act, 18 U.S.C. § 1201(a)(1) and (c), and sentenced to life imprisonment following the October 2019 abduction and murder of a three-year-old girl in Birmingham, Alabama. The sole jurisdictional hook charged in the indictment and proved at trial under § 1201(a)(1)—which applies when an offender "uses ... any means, facility, or instrumentality of interstate or foreign commerce in committing or in furtherance of the commission of the offense"—was that Brown and her co-conspirator used a Toyota Sequoia motor vehicle in a purely intrastate, non-commercial manner.

In an unpublished per curiam opinion on the Non-Argument Calendar (Judges Luck, Black, and Wilson), the Eleventh Circuit affirmed. Relying on its recent published decision in *United States v. Bryan*, 159 F.4th 1274 (11th Cir. Nov. 14, 2025), the panel held that:
1. Section 1201(a)(1)'s jurisdictional element unambiguously exercises Congress's full Commerce Clause authority over instrumentalities of interstate commerce (`Lopez` Category 2), foreclosing constitutional avoidance and the rule of lenity; and
2. Under *Bryan*, automobiles are *per se* instrumentalities of interstate commerce even when used solely intrastate.

The Question Presented is:
> "18 U.S.C. § 1201(a)(1) makes kidnapping a federal offense where the defendant uses 'any means, facility, or instrumentality of interstate or foreign commerce.' The Question Presented is whether an automobile is per se an instrumentality of interstate commerce, which would make a federal offense of every kidnapping involving an automobile."

---

## 2. Base-Rate Anchor and Procedural Signals

### Salience Band Anchor
Per `record/context.json`, this petition falls in the **`high`** salience band (`salience_score = 0.4169`), for which the 10-term lookback empirical grant rate (including summary dispositions) is **34.55%** (`0.3455`, 123 grants out of 356 high-band petitions in `metrics/statpack.md`). The overall paid-petition grant rate across all bands is **4.3%**.

### Docket and Relist History
- **Paid Petition & Counsel**: Paid petition (`No. 25-1342`) filed by experienced Supreme Court clinic counsel: Stuart Banner (UCLA Supreme Court Clinic) and Tobie J. Smith (University of Alabama Criminal Defense Clinic).
- **Amicus Support**: Two cert-stage amicus briefs were filed supporting petitioner: (1) Professor Randy E. Barnett (represented by Collin P. Wedel / Sidley Austin), and (2) the Cato Institute (Thomas A. Berry).
- **Acquiescence / Response**: The Solicitor General initially waived the right to respond on July 6, 2026; the Court requested a response on July 17, 2026; the Brief in Opposition was filed September 16, 2026.
- **Relists**: The petition was distributed for the October 30, 2026 conference, the November 6, 2026 conference, and relisted again on November 9, 2026 for the November 13, 2026 conference (`distribution_count = 3`, i.e., two relists after the initial conference).

---

## 3. Analysis of the Alleged Circuit Split and Companion Petitions

### A. The *Bryan* / *McMichael* Precedent Was Just Denied Certiorari
The single strongest empirical signal in the record comes from the direct precedent on which the unpublished panel opinion below relied: *United States v. Bryan*, 159 F.4th 1274 (11th Cir. 2025) (affirming the federal attempted-kidnapping convictions of Travis McMichael, Gregory McMichael, and William Bryan arising out of the murder of Ahmaud Arbery, where the defendants used pickup trucks intrastate).
- In *Bryan*, Judge Calvert dissented in part specifically on the ground that intrastate use of a pickup truck is not a *per se* instrumentality of interstate commerce under 18 U.S.C. § 1201(a)(1), relying on *United States v. Chavarria*, 140 F.4th 1257 (10th Cir. 2025).
- In her cert reply brief (Cert. Reply at 3), Brown herself highlighted *McMichael v. United States*, No. 25-7371 (petition filed May 5, 2026, docketed May 13, 2026), as the companion certiorari petition directly challenging the Eleventh Circuit's holding in *Bryan* on this exact issue.
- Querying the corpus (`uv run fedcourts query --court scotus --docket-number 25-7371`) reveals that the Supreme Court **denied certiorari in *Travis McMichael v. United States* (`scotus/73338271`) on October 19, 2026** after its first conference (`distributed_for_conference: 2026-10-16`, `distribution_count: 1`).
- Unlike *Brown*—which is a short, unpublished, non-argument calendar per curiam opinion that simply applies *Bryan* in two paragraphs—*McMichael* was the published lead opinion from the Eleventh Circuit with a thorough majority opinion and a detailed dissent by Judge Calvert squarely framing the issue. Yet the Court denied review in *McMichael* three weeks ago without a single relist.

### B. Shallowness of the Alleged Split with *Chavarria*
Petitioner contends that the Sixth, Seventh, and Eleventh Circuits (*United States v. Windham*, 53 F.4th 1006 (6th Cir. 2022); *United States v. Protho*, 41 F.4th 812 (7th Cir. 2022); *United States v. Bryan*, 159 F.4th 1274 (11th Cir. 2025)) conflict with the Tenth Circuit's decision in *United States v. Chavarria*, 140 F.4th 1257 (10th Cir. 2025) (Tymkovich, J.).

A full reading of *Chavarria* (CourtListener `opinion_id=11071905`) shows why the Solicitor General's distinction (BIO 10–12), while formalistic, is a major obstacle to certiorari:
1. In *Chavarria*, the government appealed the pretrial dismissal of a threadbare superseding indictment that alleged only that the defendants "used a motor vehicle, a means, facility, and instrumentality of interstate commerce," without specifying in the indictment that the vehicle was an automobile or how it was used (140 F.4th at 1259, 1264 n.14, 1267).
2. Judge Tymkovich's opinion explicitly framed the holding around the level of generality of the term "motor vehicle" in the indictment:
   - Footnote 14: *"The government attempts to move away from the superseding indictment's reference to a 'motor vehicle' by referring instead to 'automobiles.' ... 'Automobile' is considerably narrower than 'motor vehicle'—so we focus our analysis to the term 'motor vehicle,' the term used in the superseding indictment."*
   - Pages 18–20: Distinguishing *Windham* and *Protho*, the Tenth Circuit wrote: *"But even if we assumed Protho and Windham were right that cars or automobiles fit the categorical approach, that would not automatically mean that 'motor vehicles' do, too. The problem will always be the generality at which one defines the group an object belongs to. Protho resolved this by defining 'automobiles' as the relevant class for analytic purposes. The government here goes a step farther by arguing the entire universe of motor vehicles is subject to federal regulation."*
   - Conclusion (p. 23): *"We hold only that 'motor vehicles'—an undefined, generic term—are not per se instrumentalities of interstate commerce for purposes of the federal kidnapping statute."*
3. Thus, no circuit has actually reversed a conviction or dismissed an indictment that specifically alleged and proved the use of an *automobile* (here, the indictment specifically charged a "Toyota Sequoia motor vehicle," App. 12a), and the Tenth Circuit expressly reserved whether "automobiles" as a narrower class satisfy the categorical test. Moreover, the Court already denied certiorari in *Protho* (*Protho v. United States*, 143 S. Ct. 1036 (2023)) and in *McMichael* (Oct. 19, 2026).

### C. Explaining the Two Relists in *Brown*
Why has *Brown* been relisted twice (distributed for Oct. 30, Nov. 6, and Nov. 13) when *McMichael* was denied on the first conference on Oct. 19?
1. First, *Brown* features top-tier Supreme Court clinic representation (Stuart Banner) and two prominent originalist/federalism amicus briefs (Randy Barnett and the Cato Institute), and explicitly invokes Justice Thomas's recent Commerce Clause concurrence in *United States v. Hemani*, 146 S. Ct. 1677, 1695 (2026) (Thomas, J., concurring).
2. Second, Justice Thomas (potentially joined by Justice Gorsuch) has repeatedly written or joined statements respecting the denial of certiorari or dissents from the denial of certiorari in cases testing the outer bounds of the Commerce Clause. Two relists following a call for a response in a case with originalist amicus briefing and an unpublished summary affirmance below is the classic signature of a short statement respecting the denial of certiorari or a dissent from denial of certiorari being circulated, or a chamber taking a closer look before acquiescing in a denial—especially given the shallow/nascent posture of the Tenth Circuit's "motor vehicle" vs. "automobile" distinction.
3. Furthermore, as a vehicle for a merits grant, *Brown* has significant downsides: (a) the decision below is an unpublished, 4-paragraph per curiam disposition on the Non-Argument Calendar that merely cites *Bryan*; (b) the government argues (BIO 10) that Brown forfeited her statutory-interpretation argument in the district court (where she raised only a constitutional Commerce Clause challenge, see App. 12a–16a); and (c) the underlying facts involve the horrific abduction and murder of a three-year-old child at a birthday party, where state capital murder charges in Alabama were held in abeyance pending the federal prosecution (App. 11a–12a).

---

## 4. Probability Calibration

Starting from the `high` salience band base rate of **34.55%**:
- **Downward adjustments**:
  - The Court's denial of certiorari on October 19, 2026 in *McMichael v. United States* (No. 25-7371)—the published Eleventh Circuit lead case (*Bryan*) presenting the exact same question with a published dissent—strongly indicates there are not four votes to grant review on this question right now (**-22 percentage points**).
  - The alleged circuit split with *Chavarria* is shallow and arguably illusory on the face of *Chavarria*'s explicit limitation to generic "motor vehicles" as opposed to "automobiles" (**-6 percentage points**).
  - The decision below is unpublished and non-precedential, and the statutory argument faces a district-court forfeiture objection (**-3 percentage points**).
- **Upward / offsetting adjustments**:
  - The petition has been relisted twice (`distribution_count = 3`) and is supported by Stuart Banner, Randy Barnett, and the Cato Institute, indicating active interest from at least one chamber (**+8.5 percentage points**).

Balancing these factors yields a final grant probability of **0.12 (12%)** and a predicted disposition of **`denied`**.
