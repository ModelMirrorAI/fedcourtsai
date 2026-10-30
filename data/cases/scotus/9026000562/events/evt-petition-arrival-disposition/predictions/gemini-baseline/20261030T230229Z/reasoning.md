# Prediction Reasoning — `scotus/9026000562` (`evt-petition-arrival-disposition`)

## 1. Case Overview & Procedural Posture

**Case:** *James C. "Chris" McNeil, et al. v. Court of Common Pleas of South Carolina, Ninth Judicial Circuit, Charleston County*, No. 26-562  
**Event:** `evt-petition-arrival-disposition` (forecast at docketing / arrival, cutoff `2026-10-29`)  
**Originating Court:** Supreme Court of South Carolina (Appellate Case No. 2026-000919, decided May 21, 2026)  
**Segment / Fee Status:** Paid discretionary certiorari petition (`sJsonCaseType: "Paid"`), litigated *pro se* by Petitioners James C. McNeil and Meaghan Poyer.

### Background
Petitioners were month-to-month residential tenants in Charleston, South Carolina, who sued their former landlord and property managers in the Charleston County Court of Common Pleas (`No. 2025-CP-10-05095`) in September 2025. While that civil action was pending, Petitioners filed a *pro se* petition for a writ of mandamus in the original jurisdiction of the Supreme Court of South Carolina (`No. 2026-000919`) on April 14, 2026, seeking an order compelling the state circuit court to rule on their pending motions (including a motion for leave to file a second amended complaint and a motion for ADA accommodations seeking electronic filing and remote appearance). Petitioners also supplemented their mandamus filings to argue that South Carolina's electronic filing system (`SCE-File`), which restricts electronic filing access to licensed attorneys, violated the Fourteenth Amendment Due Process and Equal Protection Clauses because the clerk's paper intake scanner converted their color photographic exhibits into monochrome, non-searchable images.

On **May 21, 2026**, the Supreme Court of South Carolina issued a brief order declining to entertain the mandamus petition in its original jurisdiction, citing `Rule 245, SCACR`, and *Key v. Currie*, 305 S.C. 115, 406 S.E.2d 356 (1991), on the ground that the circuit court had already scheduled a hearing on Petitioners' motions for May 28, 2026. The court also cautioned Petitioners that their "excessive filings likely contributed to any delays in the case" (noting over forty filings in eight months) and warned them of the courts' inherent authority to impose filing restrictions on prolific or abusive filers.

Subsequently, as documented in Petitioners' own Appendix B (`App. 4–38`), the circuit court held a five-hour hearing on May 28, 2026, and entered a comprehensive order on **August 3, 2026** dismissing the entire underlying lawsuit with prejudice—both for failure to state a claim under Rule 12(b)(6) and as a severe sanction under Rule 11, SCRCP, for frivolous and abusive litigation conduct (including filing invalid subpoenas, willfully misrepresenting property claims to record *lis pendens* encumbering defendants' properties, and citing fabricated or erroneous legal authorities).

---

## 2. Base-Rate Anchor

In `record/context.json`, the pre-computed `sal-v4` salience band at arrival is **`baseline`** (`distribution_count = 0`, `cvsg_date = null`, `amicus_briefs = null`, private *pro se* petitioners).

- **Registered `cert_anchor` rate (`context.json`):** `0.05089` (~5.09%), which reflects the 10-Term pooled `reached` grant-family rate for paid petitions starting in the `baseline` band (including petitions that later acquire relists, amici, or CVSG).
- **Terminal `baseline` band rate (`metrics/statpack.md`):** Paid petitions that remain in the `baseline` band without upward trajectory signals have a historical grant-family rate of **0.6% to 1.9%** across OT2017–OT2025 (~1.2%–1.5% typical).
- **Originating court base rate (`metrics/statpack.json`):** Across 38 resolved modern discretionary cert petitions from the Supreme Court of South Carolina in the live/historical slice, **0 were granted** (`denied`: 34 [89.5%], `dismissed`: 4 [10.5%]).

Starting from the `cert_anchor` of `0.05089` (5.09%), we adjust downward substantially based on the structural, jurisdictional, and vehicle characteristics of this petition.

---

## 3. Case-Specific Signals & Downward Adjustments

1. **Pro Se Paid Petition Against a State Trial Court:**
   Although filed on the paid docket (`26-562`), Petitioners proceed *pro se* (`IsCounselofRecord: false`). Historically, *pro se* petitions—even when paid—have a vanishingly small grant rate before the Supreme Court in the absence of an unmistakable circuit split or capital/extraordinary posture. Moreover, naming the state trial court itself as the sole respondent in a collateral mandamus dispute further diminishes the likelihood of a formal merits response or Supreme Court intervention.

2. **Adequate and Independent State Law Ground / Discretionary Mandamus Refusal:**
   The judgment under review (the May 21, 2026 order of the Supreme Court of South Carolina) did not adjudicate the federal constitutional merits of South Carolina's `SCE-File` attorney-only rule. Instead, it declined to exercise original mandamus jurisdiction under `Rule 245, SCACR` and *Key v. Currie* because a hearing on Petitioners' motions was already scheduled in the trial court for May 28, 2026. A state supreme court's discretionary refusal to entertain an extraordinary writ in its original jurisdiction when ordinary trial and appellate processes are available is a classic adequate and independent state procedural ground that bars review under 28 U.S.C. § 1257(a).

3. **Mootness and Interlocutory / Collateral Posture:**
   The mandamus petition sought to compel the circuit court to rule on pending motions in `No. 2025-CP-10-05095`. As Petitioners' own appendix establishes, the circuit court held the hearing on May 28, 2026, ruled on all pending motions, and dismissed the entire action with prejudice on August 3, 2026 (denying Rule 59(e) reconsideration on August 14, 2026). The mandamus proceeding seeking to compel trial court rulings is therefore moot, and any challenge to the August 3, 2026 dismissal belongs in a direct state appeal of that final judgment, not a collateral cert petition from the earlier mandamus denial.

4. **Severe Vehicle Contamination (Rule 11 Sanctions Below):**
   Even if the Court were ever inclined to examine state court e-filing access or paper-scanning fidelity for *pro se* litigants, this record is an exceptionally poor vehicle. The trial court's August 3, 2026 order (reproduced at `App. 4–38`) dismissed Petitioners' action with prejudice as a Rule 11 sanction for egregious litigation abuse—including encumbering real property with bad-faith *lis pendens* containing willful misrepresentations, serving unauthorized subpoenas, and citing fabricated authorities—and found no medical documentation supporting an ADA disability (`App. 7–8`). Furthermore, the trial court rejected the proposed invasion-of-privacy claim based on the text of the *allegations* in the Proposed Second Amended Complaint (`App. 30`), not because of scanner quality, and independent Rule 11 sanctions disposed of the entire case regardless.

5. **Absence of Any Conflict of Authority (Rule 10):**
   Petitioners candidly acknowledge (`petition.txt` at 16–18) that no court has held that the Fourteenth Amendment requires state courts to provide direct electronic filing to *pro se* litigants or prohibits monochrome scanning of paper filings. Without a split among federal circuits or state courts of last resort, there is no basis for certiorari under Supreme Court Rule 10.

---

## 4. Probability Calibration

- **Grant Family (`granted` + `gvr`):** `0.002` (`0.2%`). There is virtually zero prospect of plenary review (`granted: 0.001`) or a grant-vacate-remand (`gvr: 0.001`) given the independent state procedural bar, mootness of the mandamus petition, absence of any split, and *pro se* sanctions posture.
- **Dismissal (`dismissed`):** `0.008` (`0.8%`). There is a small chance of administrative or Rule 46 dismissal prior to conference, though *pro se* petitioners challenging a state court directly rarely stipulate to dismissal; routine conference denial is overwhelming.
- **Denial (`denied`):** `0.990` (`99.0%`). The petition will almost certainly be denied on the first conference list on which it is considered, without a response requested.
