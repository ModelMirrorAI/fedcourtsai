# Rationale — P(grant) = 0.01

**Inputs I read.** The snapshot `2026-10-22.json` has one docket entry: the petition, filed Oct 19, 2026, with a response due Nov 20, 2026. It is a paid case. The lower court is CA5 (No. 25-11339, order dated Jul 21, 2026). I also read `context.json` (mode `forward`, band `baseline` under `sal-v4`, distribution count 0, no CVSG, Term 2026) and the provisioned `questions-presented.txt` and `petition.txt`. The petition is 42 pages and was not truncated. No BIO exists yet.

**Anchor.** This is the arrival moment and the petitioner is private: an individual against the United States. That puts the case in the private caption class, and `context.json` agrees by freezing the band as `baseline`. The prompt says to anchor on `baseline`'s bracketed `reached` rate in the statpack table "Segment base rate by salience band (sal-v4)", pooled over the Terms before 2026. The table's version matches my context. The rows for 2017–2025 run from 3.9% to 5.9%. Weighting by each row's `n` gives about **5.0%**, over roughly 12,900 weighted petitions. I left out the 2026 row because it is my own Term.

**Why I go well below the anchor.** That rate covers every paid private petition, including well-funded split petitions that later climb the salience ladder. This petition has almost none of the features that predict a grant:
- It seeks review of a **COA denial** in a § 2255 case. The CA5 order and the district court opinion are both unpublished. The district court found the motion time-barred.
- The petition **concedes there is no split**. It says the question "has not yet arisen" in these "narrow circumstances", and it cites only district-court decisions, all of them about defendants who never filed their own cert petition.
- On the merits it runs into Clay v. United States, 537 U.S. 522. Clay ties finality to the denial of the defendant's *own* petition. The petition's analogy to Rule 13(3) (rehearing by any party resets everyone's time) is creative, but no lower court is divided over it.
- The case affects one person and is fact-bound. The petitioner has already served his custodial sentence.
- Petitioner's counsel is experienced appellate counsel but not a repeat Supreme Court specialist, and no amicus support is likely.

These features usually place a paid petition far below 1–2%. I set 0.01 rather than lower to allow a small chance that the Solicitor General concedes the timeliness point, which could lead to a GVR. That is also why the summary route sits at 0.35 conditional on a grant: a confession of error is the most plausible way this case gets granted at all.

**Other claims.** `relist-increment` = 0.96, because nearly every paid petition is distributed at least once. The remaining 4% covers withdrawal or some other disposition before distribution. `cvsg-increment` = 0.002, because the United States is the respondent. `dissent-from-denial` = 0.01, because nothing here would draw a separate writing.

**Uncertainty.** I have no BIO and no lower-court text beyond the petition's own description. If the government says in a response that the motion was in fact timely, my numbers would be wrong. I also did not verify the § 2255 filing date. The district court case number (24-CV-00726) suggests the motion was filed in 2024, more than a year after Jan 23, 2023 and possibly within a year of Mar 27, 2023. That is consistent with the petition's framing. I did no live retrieval; see `retrieval.md`.
