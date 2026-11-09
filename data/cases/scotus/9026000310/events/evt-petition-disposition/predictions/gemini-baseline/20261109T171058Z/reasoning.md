# Certiorari Prediction: *Joshua F. Young v. Colorado Department of Corrections, et al.* (No. 26-310)

## Summary Forecast

- **Predicted Disposition:** `denied`
- **Grant Probability (`granted: true`):** `0.015` (1.5%)
- **Confidence Band:** `baseline` (provisioned in `context.json`)

---

## 1. Base-Rate Anchor and Procedural Posture

From `metrics/statpack.md` and `context.json`, the 10-term empirical certiorari grant rate for paid petitions in the corpus is **5.16%** (`cert_anchor.rate = 0.051588`). However, the procedural posture at the distribution moment (`2026-11-09.json`) places this petition in a substantially lower-probability conditional stratum:

1. **Waived Response and No Call for a Response (CFR):**
   - Petition for writ of certiorari was filed on September 4, 2026, and docketed on September 9, 2026 (`26-310`).
   - On October 27, 2026, Respondents (Colorado Department of Corrections, Moses "Andre" Stancil, and Jill Hunsaker Ryan, represented by the Colorado Attorney General's Office) filed a **waiver of the right to respond**.
   - On November 4, 2026, the petition was distributed for the Conference of November 20, 2026 (`distribution_count = 1`), with **no brief in opposition requested or filed** and **no amicus briefs** filed at the certiorari stage (`amicus_briefs: null`).
2. **Conditional Probability of Grant from First Distribution Following a Waiver:**
   - Under Supreme Court practice, the Court almost never grants plenary review directly from a first conference distribution when the respondent has waived a response and the Court has not yet called for a response (CFR). Even accounting for the possibility that a single Justice could request a response before or at the November 20, 2026 conference and that the petition might later be granted after a BIO is filed, the conditional probability of an eventual grant from this posture (first distribution, waived response, zero certiorari-stage amici) is well below the 5.16% unconditional paid-petition baseline—typically in the **1% to 2%** range unless there is an established circuit split or a pending merits case for which the petition is a hold candidate.

---

## 2. Case Background and Decision Below

Petitioner Joshua F. Young, a former correctional officer (Visiting Sergeant) at the Colorado Department of Corrections (CDOC), alleges that CDOC's mandatory Equity, Diversity, and Inclusion (EDI) online training program created a racially hostile work environment in violation of Title VII of the Civil Rights Act of 1964, 42 U.S.C. § 2000e-2(a)(1), and 42 U.S.C. § 1981, resulting in his constructive discharge when he resigned four months later.

This is the **second time** Mr. Young's dispute has reached the Tenth Circuit:
- **First Appeal (*Young I*, 94 F.4th 1242 (10th Cir. 2024)):** A unanimous panel (written by Judge Tymkovich, joined by Judges Matheson and Carson) affirmed the Rule 12(b)(6) dismissal without prejudice of Young's initial complaint. Although Judge Tymkovich wrote that the EDI training materials—which included a glossary defining terms like "White Fragility," "White Exceptionalism," and "BIPOC," and recommended videos on redlining and intersectionality—were "troubling on many levels" and could "set[] the stage for actionable misconduct," the panel held that a single online training program, unaccompanied by ongoing workplace harassment, ridicule, or race-based mistreatment by supervisors or coworkers, was neither sufficiently severe nor pervasive under *Harris v. Forklift Systems, Inc.*, 510 U.S. 17, 21 (1993), to alter the conditions of employment.
- **Second Appeal (*Young II*, No. 25-1068 (10th Cir. May 11, 2026)):** Rather than amending in the original action, Young filed a new lawsuit adding allegations about the "aftermath" of the training—specifically, that (1) CDOC had an ongoing commitment to annual EDI trainings; (2) employees were expected to apply the training in their work and performance reviews; (3) an unidentified officer of another race had a disciplinary sanction reversed after complaining of racism; (4) the training made Young second-guess using force and searching visitors; and (5) CDOC's Inspector General declined to investigate his internal complaint. The district court dismissed with prejudice under Rule 12(b)(6), and a unanimous Tenth Circuit panel (written by Judge Bacharach, joined by Judge Moritz and District Judge Shelby) affirmed.
- **Holding of *Young II*:** The Tenth Circuit held that even liberally construing the complaint, Young still alleged only a single computer-based training session before he resigned four months later, and did not allege a single post-training incident in which a supervisor or coworker directed racially harassing remarks at him, disciplined him, or gave him negative feedback. No petition for rehearing en banc was filed.

---

## 3. Analysis of Certiorari Criteria (Rule 10)

### A. Absence of a Circuit Split
The Petition acknowledges that "lower courts generally recite the same governing standard" from *Harris v. Forklift Systems, Inc.*, 510 U.S. 17, 21 (1993)—that workplace conduct violates Title VII when it is "sufficiently severe or pervasive to alter the conditions of the victim's employment and create an abusive working environment"—and that an isolated incident must be "extremely serious" to be actionable on its own (*Faragher v. City of Boca Raton*, 524 U.S. 775, 788 (1998)).

Rather than presenting a genuine conflict among the circuits on a question of law, the Petition argues that the courts of appeals are "uncertain" and "confused" about how to apply the "severe or pervasive" test to employer-mandated DEI trainings. However, a comparison of the appellate decisions cited in the Petition and the opinion below demonstrates doctrinal harmony applied to markedly different factual records:
- **Second Circuit (*Chislett v. New York City Dep't of Educ.*, 157 F.4th 172 (2d Cir. 2025)):** Reversed summary judgment where a white supervisor was subjected to multiple mandatory bias trainings over more than a year declaring "white culture's values" to be "supremacist" and "white toxicity in the air," **and** where racialized hostility repeatedly spilled over into daily workplace confrontations with subordinates who called her racist, told her she could not be trusted, and stripped her of supervisory duties. Notably, *Chislett* explicitly cited *Young I* (94 F.4th at 1251) with approval and agreed that implicit-bias trainings are not *per se* unlawful absent severe or pervasive spillover.
- **Ninth Circuit (*Diemert v. City of Seattle*, No. 25-1188 (9th Cir. Sept. 28, 2026)):** Retrieved via CourtListener (`opinion_id=11452678`), the Ninth Circuit's recent published opinion (which the Petition noted as then-pending) reversed summary judgment on a hostile work environment claim where the plaintiff presented evidence of ten specific race-based incidents over a five-year span—including being physically accosted by a supervisor who called him a "colonist" and blamed him for all injustices, being told by a manager that it is "impossible to be racist toward white people," being asked what he could offer as a "straight white male," and being pressured to step down from a lead role so a person of color could be promoted. Like the Tenth Circuit in *Young*, the Ninth Circuit explicitly cited *Chislett* and *Ames v. Ohio Dep't of Youth Services*, 605 U.S. 303 (2025), and held that race-conscious trainings are not inherently discriminatory unless combined with severe or pervasive workplace hostility.
- **Sixth and Seventh Circuits (*Berry v. Dep't of Corr.*, 145 F.4th 589 (6th Cir. 2025); *CBS Corp.*, etc.):** Every circuit to address the question agrees that a single mandatory diversity training session—without severe individual targeting, racial slurs directed at the plaintiff, or ongoing workplace harassment—does not by itself satisfy the *Harris*/*Faragher* severity threshold.

Thus, there is no circuit split: both conservative and liberal panels across the Second, Sixth, Ninth, and Tenth Circuits apply the exact same legal standard.

### B. Factbound Application of Settled Law and Poor Vehicle
At bottom, Petitioner asks the Court either to conduct factbound error correction on whether his First Amended Complaint pleaded enough "aftermath" to cross the plausibility threshold, or to announce a novel *per se* rule that a single online DEI training module containing controversial ideological definitions ("white fragility," "white exceptionalism," "equity") is "sufficiently severe" on its own to create an actionable hostile work environment under Title VII.

This case is also a poor vehicle for several reasons:
1. **Law-of-the-Case / Prior Unappealed Holding:** Young did not petition for certiorari from *Young I* (94 F.4th 1242 (10th Cir. 2024)), which already held that the exact same CDOC online training module, glossary, and optional videos did not by themselves constitute a severe or pervasive hostile work environment. Instead, he filed a second lawsuit attempting to plead post-training workplace effects. The Tenth Circuit in *Young II* repeatedly noted that its prior holding in *Young I* governed the training materials standing alone.
2. **Disputed Scope of Training Materials:** As the Tenth Circuit noted in footnote 3 of *Young II* (and in *Young I*), the glossary and videos at the center of Young's complaint were in an optional "Other Tools & Resources" hyperlink section created by the Colorado Department of Public Health & Environment, and the mandatory modules themselves expressly stated that employees did not need to change their personal values or beliefs.
3. **Subjective Fears Rather Than Concrete Workplace Events:** During the four months between the single online training and Young's voluntary resignation, no supervisor or colleague ever disciplined him, evaluated him poorly, or made a racially derogatory comment to him.

### C. Recent Related Certiorari Denial and Absence of Hold Candidates
- `same-question.json` confirms there are no pending or granted SCOTUS petitions sharing the same question presented (`petitions: []`).
- Corpus query (`fedcourts query --court scotus --docket-number 26-156`) shows that in *Springfield R-12 School District v. Henderson*, No. 26-156 (cited in the Petition at p. 20 n.2 as raising a related challenge arising from mandatory school-employee anti-racism training), the Court **denied certiorari on October 5, 2026** on its first conference distribution.
- While Petitioner is represented by Pacific Legal Foundation (Glenn E. Roper as Counsel of Record), which is an experienced Supreme Court litigator (having recently secured a grant in *Association for Education Fairness v. Montgomery County Board of Education*, No. 26-12, after 3 distributions and multiple amicus briefs), here there are zero amicus briefs supporting the petition, Respondents waived a response, and no CFR has issued.

---

## 4. Synthesis and Calibration

Starting from the 5.16% 10-term paid-petition base rate:
- **Downward adjustments:**
  - Respondent waived the right to respond on October 27, 2026, and the petition was distributed on November 4, 2026 for the November 20, 2026 conference with no Call for a Response (CFR) and zero certiorari-stage amicus briefs.
  - Complete absence of a circuit split; the Second (*Chislett*), Sixth (*Berry*), Ninth (*Diemert*), and Tenth (*Young I & II*) Circuits are in full agreement on the governing legal standard under *Harris* and *Faragher*.
  - Factbound Rule 12(b)(6) sufficiency issue complicated by a prior unappealed Tenth Circuit decision (*Young I*) between the same parties on the same training program.
  - No rehearing en banc sought below and no dissent on either the *Young I* (Tymkovich, Matheson, Carson) or *Young II* (Bacharach, Moritz, Shelby) panels.

Assigning a small residual probability (**1.5%**, `0.015`) accounts for the remote chance that a Justice calls for a response based on the Court's general interest in Title VII race-related litigation following *Muldrow* (2024) and *Ames* (2025) and that the case is eventually granted after further briefing. The predicted disposition is `denied`.
