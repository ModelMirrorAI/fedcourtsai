# Reasoning — Spartan Securities Group v. SEC, No. 26-341

**P(grant, any form) = 0.10.**

## Inputs read
- Snapshot `record/snapshots/2026-11-09.json` (forward mode, `cutoff: null`).
- `record/context.json`: band `baseline` (sal-v8), `distribution_count` 1, no CVSG,
  `cert_anchor.rate` 0.0516 (baseline reached rate, 10 prior Terms).
- `questions-presented.txt`, `petition.txt` (truncated at the cap; the body through
  the argument and conclusion was readable), `lower-court-docket.txt`. I did not lean on
  `decision-below.txt` beyond what the petition says about it.
- `same-question.json`: empty list, so no pending or granted companion on the same text.

## Docket posture
Paid petition from the Eleventh Circuit (published opinion, 164 F.4th 1231; rehearing en
banc petition filed and denied 2026-04-30). NCLA is counsel. The SEC (through the Solicitor
General) waived on Oct 9; the petition was distributed Oct 14 for the Nov 6 conference;
one amicus brief (Investor Choice Advocates Network) was filed Oct 15; and on **Oct 23 the
Court requested a response**, due Nov 23. So the Nov 6 distribution was overtaken. The
petition will be redistributed once the SG responds.

## Anchor and adjustments
- Anchor: the frozen baseline reached rate, **5.2%**. The statpack's ca11 row (granted 1.2%,
  GVR 2.1%) and the 1-amicus bucket (~15% grant family, n≈1159) give shape context, not the anchor.
- **Up: response requested.** A Justice asked the SG to respond after the SG waived. That is the
  Court's first sign of interest. Most such petitions are still denied, but it moves a baseline
  petition up a few points.
- **Up: QP2 is a direct follow-on to *Sripetch v. SEC* (2026).** The petition says that decision held
  the SEC need not prove pecuniary harm, and left open (a) whether disgorgement requires an
  identified victim at all and whether funds may go to the Treasury when distribution is infeasible,
  and (b) the nature of disgorgement under § 78u(d)(7). That last point drew a Thomas concurrence.
  The petition describes a split on § 78u(d)(7): the Fifth Circuit in *Hallam* treats it as legal
  disgorgement, while the Second Circuit (*Govil*/*Ahmed*) and the Ninth Circuit treat it as
  equitable. Because the Eleventh Circuit decided before *Sripetch*, a GVR for reconsideration in
  light of it is a live route, even though *Sripetch* itself went the SEC's way.
- **Down: vehicle.** The disgorgement award is small (~$150k), the stipulation on infeasibility is
  disputed as to its reasons, and the case comes after a jury trial with a fact-heavy record.
  QP1 (nonpublic statements to FINRA/DTC as "in connection with" a securities transaction) has only
  a "nascent"/"silent" split, by the petition's own description. The Court just decided a
  disgorgement case and may want a cleaner vehicle for the open questions.
- Net: about 10%, with roughly a third of that mass on a GVR rather than plenary review.

## Increments
- Relist-increment: 0.96. Once the response is filed (or its time runs out), the petition is almost
  certainly distributed again, which pushes the count past 1.
- CVSG-increment: 0.01. The SEC is the respondent, and the SG is already responding as a party.
- Dissent-from-denial: 0.10. Thomas (who wrote separately in *Sripetch* on § 78u(d)(7)) and
  Gorsuch are the plausible writers.

## Uncertainty
I don't know who requested the response or the SG's position. If the SG concedes that the
post-*Sripetch* reasoning below needs revisiting, GVR odds rise sharply. My account of *Sripetch*'s
holding comes from the petition's characterization. I did not retrieve the opinion.
