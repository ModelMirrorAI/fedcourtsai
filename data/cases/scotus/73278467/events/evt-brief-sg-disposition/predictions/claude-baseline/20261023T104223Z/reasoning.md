# Why P(grant family) = 0.82

**Inputs read.** Snapshot `2026-09-26.json` (cutoff 2026-09-26, date cut, forward mode); `context.json` (band `high` under sal-v4, distribution_count 2, CVSG 2026-06-30, paid docket); `questions-presented.txt`; the SG's invited brief (`sg-invited-brief.txt`, 28 pp., not truncated, not OCR), which I read in its recommendation, Statement, Discussion A/B and Conclusion. The petition, BIO, cert reply and appendix are provisioned, but I relied on the QP text and on the SG brief's account of them (for example, that the BIO predicted *B.P.J.* would not bear on the strip-search sub-claims). I did not read them in full. I made no CourtListener or web retrieval and did not open the case summaries directory.

**What the SG recommended.** Grant, vacate, and remand in light of *West Virginia v. B.P.J.*, 146 S. Ct. 2356 (2026), and *United States v. Skrmetti*. The SG also said plenary review is "not warranted at this time": limited percolation, no split on QP 2, and *B.P.J.*/*Skrmetti* independently foreclose the claims. The Tenth Circuit's heightened-scrutiny holding rested on *Fowler v. Stitt*, which the Court has already GVR'd after *Skrmetti*.

**Anchors.**
- Statpack CVSG cut (paid scored segment, all Terms pooled; a shape rather than a strictly-prior anchor): n=164 resolved, grant family 29.3% granted + 5.5% GVR ≈ 35%.
- Salience band `high`, bracketed `reached` rate over prior Terms 2017–2024 (2025 is this case's own docket Term): about 31–42% per Term, roughly 37% pooled.

Both anchors pool cases where the SG recommended denial, which is the majority of CVSGs. Neither table splits the population by recommendation, so the move from about 35% up to 82% is my judgement. It rests on the following:
1. The Court historically follows an SG recommendation at a high rate, and a GVR recommendation in light of a new controlling decision is the easiest kind to follow.
2. The posture strongly suggests the Court has been waiting on this: distributed for December 2025, then dormant until a June 29, 2026 conference right after *B.P.J.* came down, consistent with a hold for *B.P.J.*
3. The petitioners, who are the losing party below, plainly want the judgment vacated. A GVR costs the Court nothing, and it has used GVRs for other post-*Skrmetti* transgender-classification cases (*Kadel*, *Fowler*).

**Discounts.**
- The Court did not GVR on its own after *B.P.J.*. It chose to CVSG instead, which signals that at least some Justices doubted that *B.P.J.* clearly controls. The likely doubts are the prison and Turner context, and the Tenth Circuit's sex-classification rationale as distinct from transgender status.
- Respondent will file a supplemental brief opposing a GVR.
- An outright denial with a dissent remains live.

Hence about 0.18 on denial, rather than the 0.1 a routine SG-GVR recommendation might warrant.

**Claims.**
- `summary-disposition-route` 0.85 (conditional on a grant): plenary review is the minority grant path given the SG's position.
- `relist-increment` 0.95: from a count of 2, a post-brief distribution is nearly automatic.
- `cvsg-increment`: vacuous (a CVSG is already on the docket); stated at 0.01.
- `dissent-from-denial` 0.45 (conditional on a denial): a denial would leave an adverse published decision against 23 amicus states, and Justices Alito and Thomas frequently write in that posture.

**Where to discount me.** Two weaknesses: I have no committed rate split by SG recommendation, and I rely on my own sense of how often the Court follows such recommendations.
