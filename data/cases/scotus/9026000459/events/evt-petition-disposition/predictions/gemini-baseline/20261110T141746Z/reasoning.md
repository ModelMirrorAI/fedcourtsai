# Prediction Reasoning: *Marshall Grace v. United States* (No. 26-459)

- **Case ID**: `scotus/9026000459`
- **Event ID**: `evt-petition-disposition` (`stage: cert`, `kind: petition`, `moment: distribution`)
- **Input Snapshot**: `2026-11-10.json`
- **Prediction**: `denied` (`granted: 0`, `probability: 0.035`)

---

## 1. Executive Summary

Petitioner Marshall Grace seeks a writ of certiorari—or, in the alternative, a grant, vacatur, and remand (GVR) in light of *Pitchford v. Cain*, 608 U.S. 391 (2026)—from a published Fifth Circuit decision affirming his federal drug-trafficking convictions and mandatory minimum 120-month sentence (*United States v. Grace*, 169 F.4th 359 (5th Cir. 2026)). The petition asks whether a federal appellate court, after concluding that a federal district court deviated from the three-step framework of *Batson v. Kentucky*, 476 U.S. 79 (1986), by questioning a prospective juror *sua sponte* rather than evaluating solely the prosecutor's stated reason, may nevertheless affirm the denial of the *Batson* challenge on the existing record rather than remanding for further step-three findings.

Both empirical base rates and case-specific legal and vehicle considerations point overwhelmingly toward a denial of certiorari:
1. **Procedural Signals**: The Solicitor General waived the United States' right to respond on November 3, 2026, and the petition was distributed on November 9, 2026, for the November 25, 2026 Conference (`distribution_count: 1`) with no amicus support (`amicus_briefs: null`) and no call for a response (CFR).
2. **Inapplicability of *Pitchford v. Cain* (GVR Unlikely)**: *Pitchford* (decided May 28, 2026, three weeks after the Fifth Circuit denied rehearing in *Grace*) held on federal capital habeas review that the Mississippi Supreme Court unreasonably determined that defense counsel had *waived* his *Batson* step-three pretext argument where the state trial judge twice cut off counsel and never conducted step three. Here, by contrast, defense counsel was given a full opportunity to argue pretext before and after the district judge questioned Juror 8 (Edward Davis), the Fifth Circuit did not find waiver, and the Solicitor General has waived response rather than confessing error or acquiescing in a GVR.
3. **Illusory Split and Severe Vehicle Defects (Plenary Review Unlikely)**: Even before calling Juror Davis to the bench, the district court explicitly rejected defense counsel's primary step-three argument that the government was systematically targeting Black venirepersons ("Well, I disagree with that. They're not."). Defense counsel offered no comparative juror analysis showing that similarly situated non-Black jurors with large families were retained. Moreover, when questioned by the district court, Juror Davis revealed that he had failed to disclose during earlier voir dire that his son had served two-and-a-half years in jail and five years on probation for a firearm offense, doubted his son was treated fairly, and stated, "only God can judge people. You know, I can't really judge nobody." Any remand would be an exercise in futility.

Accordingly, I estimate a **3.5% probability (`0.035`)** of a favorable cert disposition (`1.0%` plenary grant + `2.5%` GVR) and a **96.5% probability** that certiorari is **denied**.

---

## 2. Base Rates and Procedural Posture

### Empirical Priors (`metrics/statpack.md` & `context.json`)
- **Salience Band Anchor (`band: "baseline"`, `sal-v8`)**: In `record/context.json`, the frozen `cert_anchor` rate—pooling the bracketed `reached` rate for `baseline` paid petitions under `sal-v8` across the 9 strictly prior Terms (`OT2017–OT2025`, `n = 12,658`) in `metrics/statpack.md`—is **5.16%** (`0.051588`). Petitions that *end* in the `baseline` band without ever being relisted or drawing a response request grant at roughly **1.4%–1.5%** (`denied 97.3%, dismissed 1.3%, granted 0.8%, gvr 0.6%` over `n = 11,020` resolved in `Cert petitions by salience band`).
- **Relist and CVSG Cuts (Paid Scored Segment)**:
  - In `Cert petitions by relist count (paid scored segment)`, petitions with `relist_bucket = 0` (`n = 10,204` resolved) have a grant-family rate of **1.8%** (`denied 96.8%, dismissed 1.3%, granted 1.3%, gvr 0.5%`), compared with **13.5%** at `1` relist (`n = 2,532`, `granted 8.3%, gvr 5.2%`), **41.2%** at `2` relists (`n = 495`, `granted 28.3%, gvr 12.9%`), and **37.3%** at `3+` relists (`n = 483`, `granted 23.2%, gvr 14.1%`).
  - In `Cert petitions by CVSG status (paid scored segment)`, petitions with no CVSG (`n = 13,550` resolved) have a **6.4%** grant-family rate (`denied 92.4%, granted 4.1%, gvr 2.3%`), versus **34.8%** with a CVSG (`n = 164`). Here the United States is the respondent, so a CVSG is inapplicable.
- **Amicus Count Cut (Paid Scored Segment)**: In `Cert petitions by amicus-brief count (paid scored segment)`, petitions with `0` amicus briefs (`n = 11,109` resolved) have a **3.8%** grant-family rate (`denied 95.0%, granted 2.0%, gvr 1.8%, dismissed 1.3%`), compared to **14.9%** with `1` amicus brief (`n = 1,159`) and **22.7%** with `2+` amicus briefs (`n = 1,446`).
- **Originating Circuit (`ca5`)**: In `Modern cert petitions by originating circuit`, Fifth Circuit petitions (`n = 5,418` resolved) have a **3.9%** grant-family rate (`denied 94.6%, gvr 2.3%, dismissed 1.6%, granted 1.6%`).
- **Conditioning Adjustment from the `5.16%` Anchor**: Starting from the `5.16%` `baseline` reached anchor, I adjust downward to **3.5%** (`0.035`) because (a) the Solicitor General waived a response on November 3, 2026 rather than filing a BIO or acquiescing in a remand, (b) zero amicus briefs were filed (`3.8%` terminal base rate for 0-amicus paid petitions), and (c) the record reveals severe vehicle defects that make both a CFR and a GVR in light of *Pitchford v. Cain* unlikely.

---

## 3. Factual and Procedural Background (Provisioned Record)

All provisioned filings in `record/documents/` (`petition.txt`, `questions-presented.txt`, `appendix.txt`, `decision-below.txt`, and `lower-court-docket.txt`, none with `empty_text` or `ocr_derived`) were reviewed alongside `record/snapshots/2026-11-10.json`.

In July 2020, following a DEA investigation and a traffic stop in New Orleans, officers recovered approximately 441 grams of methamphetamine from Marshall Grace's trunk. Grace signed a written statement admitting ownership of the drugs and admitting that he purchased eight ounces of methamphetamine monthly for two years to supply two local dealers. He was convicted by a jury in the Eastern District of Louisiana of conspiracy to distribute 500 grams or more of methamphetamine (21 U.S.C. § 846) and possession with intent to distribute 50 grams or more of methamphetamine (21 U.S.C. § 841(a)(1), (b)(1)(B)), and sentenced to the statutory mandatory minimum of 120 months' imprisonment.

During jury selection on August 12, 2024, 31 prospective jurors were examined, five of whom were Black (App. 3a). Ultimately, two Black jurors (Juror 1 and Juror 29) were seated on the 12-person jury and one Black juror (Juror 32) served as an alternate (App. 5a, 17a–18a). The Government exercised two of its six peremptory strikes against Black venirepersons:
1. **Juror 14 (Mr. White)**: The Government's first peremptory strike, exercised after the district court denied a close for-cause challenge; Grace did not challenge this strike on appeal (App. 3a n.2, 16a).
2. **Juror 8 (Edward Davis)**: The Government's fourth peremptory strike (after striking two white males with its second and third strikes, and followed by striking two more non-Black jurors with its fifth and sixth strikes, App. 17a).

When defense counsel raised a *Batson* challenge, the prosecutor explained that "there wasn't much to go on for Mr. Davis except for the fact that we knew he had seven sons and based on that information and not knowing much else about him, we chose that he would probably not be a great juror for the government" (App. 15a). The prosecutor also argued that the strike pattern across the panel as a whole (retaining Jurors 1 and 29 and striking four non-Black jurors) negated any inference of racial discrimination (App. 16a–18a).

Defense counsel responded at step three by arguing (1) that striking two of the available Black jurors established that the Government "unfairly targeted black people" (App. 18a), and (2) that given Davis's apparent age, his seven sons were likely adults rather than young children at home (App. 19a). Crucially:
- The district court **explicitly rejected** defense counsel's claim that the prosecutors targeted Black jurors: `"THE COURT: Well, I disagree with that. They're not. I disagree with that."` (App. 18a).
- However, because the district judge remained uncomfortable with the "seven sons" explanation standing alone, the court called Juror Davis to the bench to ask him about his family "for the record purposes" (App. 18a–20a).
- During that colloquy, Juror Davis revealed that one of his sons had spent two-and-a-half years in pretrial detention in Baton Rouge and five years on probation on a gun charge, that he felt his son had not been treated fairly, and that when asked if he could be fair and impartial as a juror, `"Well, to me, you know, only God can judge people. You know, I can't really judge nobody. Only God can judge people."` (App. 21a–22a).
- Both the prosecutor and the district court noted on the record that the court had previously asked the venire whether any family members had been arrested, and Juror Davis had remained silent and "was less than candid" (App. 23a–24a).

On appeal, the Fifth Circuit (Stewart, J., joined by Jones and Willett, JJ., 169 F.4th 359 (5th Cir. Mar. 27, 2026)) admonished the district court for questioning Davis *sua sponte* to supply a race-neutral justification rather than evaluating the prosecutor's articulated reason (App. 10a–11a). Even so, the panel held that the district court did not commit clear error in denying the *Batson* challenge because, setting aside the *sua sponte* colloquy, Grace bore the step-three burden of proving purposeful discrimination under *Purkett v. Elem*, 514 U.S. 765, 768 (1995), and *Davis v. Ayala*, 576 U.S. 257, 271 (2015), and failed to meet it: two Black jurors and one Black alternate were empaneled (which, as the district court recognized, undermined Grace's claim of a system to violate *Batson*), and Grace failed to show that the prosecutor's race-neutral reason of having seven sons was pretextual (App. 11a–12a). Panel rehearing was denied on May 5, 2026 (App. 26a; `lower-court-docket.txt` confirms no en banc poll was recorded).

---

## 4. Legal Analysis: Why Neither a GVR Nor Plenary Review Is Likely

### A. Why a GVR in Light of *Pitchford v. Cain* Is Unlikely
Petitioner argues that because the Fifth Circuit denied rehearing on May 5, 2026, and this Court decided *Pitchford v. Cain*, 608 U.S. 391, on May 28, 2026, the Court should GVR. That argument is unlikely to succeed for three reasons:
1. **Doctrinal Distance**: *Pitchford* was a 5–4 capital habeas decision (Kavanaugh, J., joined by Roberts, C.J., and Sotomayor, Kagan, and Jackson, JJ.; Gorsuch, J., dissenting, joined by Thomas, Alito, and Barrett, JJ.) holding that the Mississippi Supreme Court unreasonably applied clearly established federal law under 28 U.S.C. § 2254(d) when it held that defense counsel *waived* his *Batson* step-three pretext argument even though the state trial court twice cut off defense counsel from speaking and "full-stop ended its *Batson* analysis at step two." *Pitchford* did not address—much less alter—the standard governing when a federal appellate court on direct review may affirm a *Batson* ruling where the defendant had a full opportunity to argue pretext but failed to proffer comparative juror evidence or carry his step-three burden of persuasion.
2. **No Denial of Opportunity to Rebut or Waiver Holding Below**: Unlike in *Pitchford*, Grace's trial counsel was given a complete opportunity to argue pretext both before and after Juror Davis was questioned (App. 17a–19a, 22a–23a), and the Fifth Circuit decided step three on the merits rather than finding waiver.
3. **Solicitor General's Waiver**: When a newly decided Supreme Court case genuinely calls a federal criminal affirmance into question, the Solicitor General typically files a brief acquiescing in a GVR (or the Court calls for a response to obtain the Government's view). Here, the Solicitor General waived a response outright.

### B. Why Plenary Review of the Question Presented Is Unlikely
1. **No Genuine Rule-of-Law Conflict**: Petitioner frames the Fifth Circuit's decision as an outlier under *Pullman-Standard v. Swint*, 456 U.S. 273 (1982), and step-three remand cases such as *United States v. McAllister*, 693 F.3d 572 (6th Cir. 2012), and *Salters v. New York City Transit Authority*, No. 25-383 (2d Cir. Aug. 7, 2026). In those cases, however, the trial court completely omitted step three in the face of concrete evidence of pretext (such as comparative juror evidence or multiple unexplained strikes), leaving unresolved credibility questions. Here, the Fifth Circuit expressly applied *Flowers v. Mississippi*, 588 U.S. 284 (2019), *Miller-El v. Dretke*, 545 U.S. 231 (2005), and its own en banc precedent in *Chamberlin v. Fisher*, 885 F.3d 832 (5th Cir. 2018), and concluded only that *Grace himself* failed to carry his step-three burden of persuasion on the undisputed record.
2. **Severe Vehicle Flaws**:
   - **Pre-Colloquy Finding by the District Judge**: Before calling Juror Davis to the bench, the district judge expressly rejected defense counsel's core step-three contention that the prosecutors were targeting Black jurors (`"THE COURT: Well, I disagree with that. They're not. I disagree with that."` App. 18a), relying on the fact that only two Black jurors were struck (one after a close for-cause challenge) while two Black jurors and one Black alternate were seated.
   - **Zero Comparative Juror Evidence**: Defense counsel never identified a single non-Black juror with a similarly large family who was kept by the prosecution, nor did counsel ask to question the prosecutor or supplement the record.
   - **Futility of Remand**: Even if the case were remanded for a reconstruction hearing limited to the prosecutor's pre-colloquy state of mind, the record now establishes that Juror Davis failed to disclose his son's 2.5-year incarceration during general voir dire ("was less than candid," App. 24a) and declared that "only God can judge people. You know, I can't really judge nobody" (App. 22a). The Supreme Court does not expend its scarce merits docket on fact-bound criminal appeals where a remand could not possibly alter the outcome.

---

## 5. Probability and Claims Calibration

- **`disposition` / `probability` (`0.035`)**: Decomposed into a `0.025` (2.5%) probability of a GVR in light of *Pitchford v. Cain* and a `0.010` (1.0%) probability of a plenary grant (`0.965` probability of `denied`).
- **`relist-increment` (`0.08`)**: Probability that the petition is distributed at least once more after its initial November 9, 2026 distribution (primarily if a Justice calls for a response from the Solicitor General).
- **`cvsg-increment` (`0.001`)**: Minimal floor; the United States is already the respondent.
- **`summary-disposition-route` (`0.714`)**: Conditional on a grant (`0.035`), the probability that the Court disposes of the petition in the cert order itself via a GVR in light of *Pitchford v. Cain* (`0.025 / 0.035 = 0.714`) rather than setting the case for plenary briefing and oral argument (`0.286`).
- **`dissent-from-denial` (`0.02`) & `order-writers`**: Small (~2%) probability that a Justice (most plausibly Justice Sotomayor at `0.01` or Justice Jackson at `0.01`) authors a dissent or statement respecting the denial of certiorari.
- **`big_case_score` (`0.15`)**: Modest doctrinal significance if decided on the merits—clarifying appellate remand standards for *Batson* step-three procedural errors under *Pullman-Standard v. Swint*—in a routine single-defendant federal drug appeal.
