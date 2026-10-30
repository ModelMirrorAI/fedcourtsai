# Prediction Reasoning: *Shannon Cross v. Central Contra Costa Transit Authority* (No. 26-100)

- **Case ID:** `scotus/9026000100`
- **Event ID:** `evt-order-call-for-response-disposition` (`moment: response-requested`)
- **Snapshot Date:** `2026-08-13` (cutoff `2026-08-14`)
- **Predicted Disposition:** `denied` (`granted: false`, grant-family probability = `0.045`, comprising `granted: 0.030` and `gvr: 0.015`)

---

## 1. Question Presented and Procedural Posture

Petitioner Shannon Cross, a Muslim bus operator employed by Respondent Central Contra Costa Transit Authority (CCCTA), was terminated in June 2019 following a collision between her bus and a bicyclist, roughly three and a half months after receiving written approval to wear a hijab on duty and after complaining to human resources that two supervisors told her she could not wear her hijab ("that" / "that thing") and announced strict enforcement of the no-hat policy in the breakroom.

Cross sued CCCTA in the Northern District of California asserting claims for religious discrimination, retaliation, and hostile work environment under Title VII (42 U.S.C. §§ 2000e-2, 2000e-3) and California's Fair Employment and Housing Act (FEHA). Judge Jon S. Tigar granted summary judgment to CCCTA on all claims on September 3, 2024 (`2024 U.S. Dist. LEXIS 252435`, App. 9a–27a), and a Ninth Circuit panel (Judges Nguyen and Bennett, with District Judge Matsumoto sitting by designation) unanimously affirmed without oral argument in a short, unpublished memorandum disposition on January 13, 2026 (`2026 U.S. App. LEXIS 788`, App. 1a–8a), denying rehearing and rehearing en banc on February 20, 2026 (App. 28a–29a).

After Justice Kagan granted an extension of time (No. 25A1259), Cross filed her petition for a writ of certiorari on July 20, 2026 (docketed July 22, 2026). The petition frames a broad doctrinal challenge:

> Whether the judicially-imposed application of the *McDonnell Douglas* burden-shifting framework at summary judgment in a Title VII religious discrimination case — where the employer pressured the plaintiff to abandon her religious practice of wearing a hijab, terminated her based on a purported reason contradicted by objective video evidence, and imposed uniquely harsh discipline not given to any similarly situated employee — led the courts below to credit the employer's disputed account, in a manner incompatible with Rule 56 and this Court's decisions.

Respondent CCCTA waived its right to respond on July 24, 2026, and the petition was distributed on July 29, 2026 for the September 28, 2026 Long Conference (`distribution_count: 1`). On August 13, 2026, the Court requested a response (due September 14, 2026). We forecast the petition's disposition from the August 13, 2026 snapshot immediately following the Call for a Response (CFR).

---

## 2. Base-Rate Anchor

From `record/context.json`, this paid petition carries frozen salience band `baseline` under `sal-v4` (`term: 2026`, `distribution_count: 1`, `amicus_briefs: null` / zero amicus filings on the docket as of August 13, 2026).

Anchoring on `metrics/statpack.md`:
1. **Salience-band base rate (`baseline`, `sal-v4`):**
   - Across the pooled modern discretionary-cert live/historical slice, resolved paid petitions ending in the `baseline` band (n = 9,936) have a grant-family rate of **1.2%** (`denied` 97.5%, `dismissed` 1.3%, `granted` 0.8%, `gvr` 0.4%).
   - Because `band: "baseline"` is frozen at the prediction snapshot (`moment: response-requested`), the scored reference is the **risk-set (`reached`) denominator**—every paid petition that started in `baseline`, including those that later escalated into `elevated` or `high` via a Call for a Response or relists. Across recent complete Terms in `metrics/statpack.md`, the `baseline [reached]` grant-family rate is:
     - **OT2025:** 4.0% (n = 1,314; terminal `baseline` 1.0%, n = 994)
     - **OT2024:** 5.9% (n = 1,274; terminal `baseline` 1.4%, n = 936)
     - **OT2023:** 5.9% (n = 1,312; terminal `baseline` 1.7%, n = 958)
     - **OT2022:** 5.9% (n = 1,196; terminal `baseline` 1.3%, n = 894)
     - **OT2021:** 5.7% (n = 1,500; terminal `baseline` 1.2%, n = 1,158)
2. **Originating circuit (`ca9`):**
   - Modern cert petitions from the Ninth Circuit (denial-reweighted, n = 5,577 resolved) resolve at `denied` 94.8%, `granted` 2.1%, `dismissed` 1.9%, `gvr` 1.1% (grant-family rate **3.2%**; unweighted live/historical slice **6.0%**).
3. **Zero cert-stage amicus briefs (`cert_amicus = 0`):**
   - Paid petitions with zero amicus briefs (n = 11,109) resolve at `denied` 95.0%, `granted` 2.0%, `gvr` 1.8%, `dismissed` 1.2% (grant-family rate **3.8%**).
4. **Conditioning on the Call for a Response (CFR):**
   - A Call for a Response after a respondent's waiver is a meaningful positive selection signal: it removes the petition from the near-zero grant-rate pool of unrequested waivers and places it into the actively scrutinized tier (analogous to the `elevated` salience band, where terminal grant + GVR is 6.6% + 3.7% = **10.3%** overall across the live/historical slice, and 7.8%–13.4% across OT2022–OT2025). Even within the CFR cohort, however, roughly 88%–91% of petitions are denied once the brief in opposition is filed.

Starting from an unconditional `baseline [reached]` anchor of ~4.5%–5.5% and an average post-CFR conditional rate of ~8%–10%, we adjust for the specific legal, institutional, and vehicle characteristics of No. 26-100.

---

## 3. Case-Specific Signals

### A. Upward Signals (Why a Response Was Called For)

1. **Known Two-Justice Interest in Reconsidering *McDonnell Douglas* at Summary Judgment:**
   - Justice Thomas, joined by Justice Gorsuch, recently dissented from the denial of certiorari in *Hittle v. City of Stockton*, 145 S. Ct. 759 (2025) (No. 24-427, cert. denied Mar. 10, 2025)—another Ninth Circuit Title VII religious-discrimination case affirmed on summary judgment—arguing that the *McDonnell Douglas* framework distorts Rule 56 analysis.
   - Three months later, in *Ames v. Ohio Department of Youth Services*, 605 U.S. 303, 319–26 (2025) (No. 23-1039), Justice Thomas (again joined by Justice Gorsuch) wrote a separate concurrence reiterating that the Court has never squarely decided whether *McDonnell Douglas* is an appropriate tool for evaluating Title VII claims at summary judgment and inviting a future vehicle raising the question.
   - Chief Judge Elrod's January 2026 concurrence in *Awe v. Harris Health System*, 163 F.4th 969, 975 (5th Cir. 2026), spotlighted that invitation, and the petition here was drafted specifically around *Ames*, *Hittle*, and *Awe*, adding arguments under *Bostock v. Clayton County*, 590 U.S. 644 (2020), and *EEOC v. Abercrombie & Fitch Stores, Inc.*, 575 U.S. 768 (2015).
   - Because CCCTA waived a response on July 24, 2026, a chamber interested in the *McDonnell Douglas* issue (most likely Justice Thomas's or Justice Gorsuch's) needed to call for a response so the case could be evaluated with adversarial briefing at the Long Conference.
2. **Co-Counsel Signal:**
   - While the petition was filed by Cross's trial/appellate counsel (Jeremy L. Friedman) and the Church State Council, the Supreme Court docket snapshot reflects that Kelly J. Shackelford of First Liberty Institute entered an appearance for Petitioner, signaling institutional religious-liberty attention.

### B. Downward Signals (Why Certiorari Will Almost Certainly Be Denied After the BIO)

Despite the CFR, the record in the petition appendix reveals severe vehicle defects and alternative grounds that make this case far weaker than *Hittle*—which itself failed to attract four votes:

1. **Recent Denial in *Hittle* (No. 24-427) and Restraint in *Ames* (No. 23-1039):**
   - In *Hittle v. City of Stockton*, the petition challenged a **published** Ninth Circuit opinion (101 F.4th 1000), was litigated by experienced Supreme Court counsel (Aaron Streett), attracted **10 amicus briefs**, and was distributed **5 times** before being denied on March 10, 2025, with only Justices Thomas and Gorsuch noting dissent.
   - In *Ames* (decided June 5, 2025), the full Court unanimously rejected the Sixth Circuit's heightened "background circumstances" rule within the first step of *McDonnell Douglas* while declining to disturb the *McDonnell Douglas* framework itself; seven Justices declined to join the Thomas/Gorsuch concurrence questioning *McDonnell Douglas* wholesale.
   - There is no indication that two additional Justices have become eager to upend 50 years of Title VII summary-judgment practice barely a year after *Hittle* and *Ames*.
2. **Unpublished, Non-Precedential Memorandum Disposition:**
   - Unlike *Hittle*, the Ninth Circuit decision below is a brief, unpublished memorandum disposition (`2026 U.S. App. LEXIS 788`) issued without oral argument four days after submission. It establishes no circuit law and creates no circuit split.
3. **Heavy Factual Disputes, Signed Admission of Fault, and Multiple Performance Infractions:**
   - Although the petition portrays the case as one where *McDonnell Douglas* forced the courts below to ignore video and expert evidence of a blameless bus driver, the District Court and Ninth Circuit opinions (App. 4a–6a, 11a–13a, 18a–25a) document multiple independent, fact-bound hurdles that CCCTA's Brief in Opposition will foreground:
     - **Police Report and Cross's Written Admission of Fault:** The investigating police department determined that Cross was 100% at fault for the bicycle collision and violated California Vehicle Code § 21760(b) (three-foot safe passing distance). Moreover, prior to the grievance hearing, Cross submitted a signed statement acknowledging that she was "at complete fault" for the collision (App. 6a, 18a, 43a ¶ 69).
     - **Additional On-Video Safety Violations:** When Cross claimed at her *Skelly* hearing that a bus alarm had distracted her and that she had a clean driving record, CCCTA reviewed additional bus video at the union's request. That review showed no alarm at the time of the crash, and instead revealed Cross running 30 stop signs and red lights, using her cell phone while the bus was in revenue service, and failing to stop at BART crosswalks (App. 6a, 12a, 21a–22a).
     - **Honest-Belief Rule on Pretext:** On the retaliation claim, CCCTA *conceded* that Cross established a *prima facie* case under *McDonnell Douglas* (App. 21a), so the prima facie requirement did no work at all. Summary judgment rested on the settled principle (*Villiarimo v. Aloha Island Air, Inc.*, 281 F.3d 1054, 1063 (9th Cir. 2002)) that even if a plaintiff disputes the objective accuracy of the underlying charge (via a retained bicycle expert years later), pretext turns on whether the employer *honestly believed* its stated reasons at the time of termination—which was supported here by the contemporaneous police determination, on-board video review by three levels of management (Glenn, Rettig, Churchill), Cross's own admission of fault, and the union's decision not to take the grievance to arbitration (App. 22a–25a).
     - **Comparator Dissimilarities and a Muslim Comparator:** Cross's primary comparator (Ronnette Brown) had worked for CCCTA for over 25 years (Cross had worked there less than a year), and the police found the bicyclist—not Brown—at fault in Brown's accident (App. 4a–5a, 18a–19a). As for the other drivers who received last-chance agreements for collisions with stationary objects or trucks, none struck a bicyclist or pedestrian, and CCCTA submitted declaration evidence that at least one of those retained comparators is himself a practicing Muslim (App. 19a, citing Sadat Decl.), cutting directly against an inference of anti-Muslim animus.
4. **Pleading and Preservation Obstacles on the *Abercrombie* / Accommodation Theory:**
   - Section IV of the petition argues that the decision below conflicts with *EEOC v. Abercrombie & Fitch Stores, Inc.*, 575 U.S. 768 (2015), because Cross's accommodation was allegedly ineffective. Yet the District Court noted that CCCTA *approved* Cross's written request to wear her hijab in February 2019, emailed all supervisors of that approval, and reminded Supervisor Morris when Cross complained (App. 10a–11a)—and, critically, that Cross **never pleaded a failure-to-accommodate claim in her complaint** (App. 20a n.2). Similarly, her unpleaded "quid pro quo religious harassment" theory was disposed of in a single footnote because neither supervisor conditioned any job benefit on renouncing her faith (App. 8a n.1, 27a n.4).
5. **No Amicus Support at the Cert Stage:**
   - Unlike *Hittle* (10 cert-stage amicus briefs) and *Ames* (substantial amicus participation), zero amicus briefs had been filed in No. 26-100 by the August 13, 2026 CFR date (when the initial August 21 response deadline was only eight days away).

---

## 4. Main Counter-Argument and Synthesis

**What would have to happen for a grant or GVR?**
The strongest path to a grant-family outcome is either:
1. Justices Thomas and Gorsuch persuade two colleagues (for instance, Justices Alito and Kavanaugh, given Kavanaugh's D.C. Circuit opinion in *Brady v. Office of the Sergeant at Arms*, 520 F.3d 490 (D.C. Cir. 2008), criticizing the *McDonnell Douglas* prima facie step) that the lower courts' rigid bifurcation of "direct" versus "circumstantial" evidence and compartmentalization of harassment evidence away from the termination inquiry warrants plenary review; or
2. Following the Brief in Opposition, the Court holds or GVRs the petition if another cleaner Title VII / *McDonnell Douglas* case is granted during OT2026, or issues a summary GVR instructing the Ninth Circuit to consider the harassment and comparator evidence holistically.

**Why that remains unlikely (`probability = 0.045`):**
Even Judge Kavanaugh's critique in *Brady* focused on skipping the *prima facie* step once the employer proffers a legitimate, non-discriminatory reason and asking directly whether a reasonable jury could find pretext/discrimination on the whole record—which is exactly what both courts below already did on Cross's retaliation claim (where the prima facie case was undisputed and Cross still lost on step three because of the police report, her admission of fault, and the video of 30 traffic violations). A vehicle in which a public-transit bus driver hit a bicyclist, was found at fault by the police, signed a letter admitting fault, and was caught on video rolling through 30 stop signs/red lights and using a cell phone while driving a bus is an exceptionally poor candidate for plenary review or summary reversal. Once CCCTA's Brief in Opposition lays out those record facts alongside the unpleaded accommodation claim and the retained Muslim comparator, the overwhelming likelihood is a routine denial of certiorari (possibly with a brief statement or noted dissent by Justice Thomas and/or Justice Gorsuch, or without comment).

Accordingly, we set the grant-family probability at **4.5% (`0.045`)**, split between **3.0% (`0.030`)** for plenary `granted` and **1.5% (`0.015`)** for `gvr`, with **93.5% (`0.935`)** on `denied`, **1.5% (`0.015`)** on `dismissed`, **0.3% (`0.003`)** on `withdrawn`, and **0.2% (`0.002`)** on `other`.
