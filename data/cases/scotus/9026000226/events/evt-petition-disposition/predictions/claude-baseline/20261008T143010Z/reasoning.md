# Rationale for the numbers: Mast v. Doe, No. 26-226

## Inputs read

- Snapshot `record/snapshots/2026-10-08.json` (the file `context.json` names).
  Paid petition docketed August 21, 2026 from the Fourth Circuit (No. 24-1900,
  decided April 22, 2026, rehearing denied May 20, 2026). Three docket entries:
  petition filed August 18, respondents' waiver filed September 4, distributed
  September 30 for the October 16, 2026 conference. No amici, no response, no CVSG.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`,
  `distribution_count` 1, `cvsg_date` null, term 2026, `signals_observable` true,
  cutoff null.
- `record/documents/questions-presented.txt` and `petition.txt` (134 pages, the
  text file is truncated; I read the related-proceedings list, the statement, the
  full reasons-for-granting section, and the appendix excerpts of the Fourth Circuit
  majority and Judge King's dissent). No brief in opposition exists because
  respondents waived.

## Anchor

The frozen band is `baseline` and the statpack's band table is computed under
`sal-v4`, the same version as my context, so the table is my anchor. Pooling the
bracketed `reached` figure for `baseline` over the nine prior Term rows the table
renders (OT2017 through OT2025, n from 1140 to 1739 per Term) gives roughly 5.0%
(about 637 weighted grants over 12,720 weighted petitions that reached the band).
That is the rate a privately captioned paid petition at its first distribution
actually faces, and it is the yardstick I am scored against.

For shape rather than level I also read the relist-count cut (relist 0 grants about
1.2% plus 0.5% GVR; relist 1 about 8% plus 5%), the CVSG cut (no CVSG: 4.0% granted
plus 2.3% GVR), and the originating-circuit cut (ca4: 1.3% granted plus 1.2% GVR,
slightly below the ca2/ca9/cadc rates).

## Adjustments from 5% to 11%

Upward:

- **Counsel and presentation.** Counsel of record is a McGuireWoods Supreme Court
  practitioner with a former state solicitor general as co-counsel. The petition is
  well built: it leads with a party-presentation claim, cites the Court's two recent
  reversals of the Fourth Circuit on exactly that principle (Clark v. Sweeney, 2025;
  Margolin v. National Association of Immigration Judges, 2026), and offers a GVR in
  light of Margolin as a fallback. Margolin post-dates both the panel decision and
  the rehearing denial, which is the classic GVR fact pattern, and it gives the
  Court a cheap way to act if it is inclined to.
- **Published, divided opinion in a First Amendment posture.** The panel held the
  order a content-based prior restraint and sustained it under strict scrutiny on a
  national-security rationale it acknowledged, in a footnote, the district court had
  not adopted. A prior restraint sustained on a rationale no party briefed is an
  unusual appellate product, and the Court has shown repeated appetite for policing
  the Fourth Circuit's party-presentation practice.
- **Public profile.** The underlying custody dispute has drawn sustained national
  coverage, which raises the odds that a Justice or clerk looks closely.

Downward:

- **Interlocutory posture with a live jurisdictional dissent.** Judge King would
  have dismissed the appeal for want of jurisdiction under 28 U.S.C. 1292(a)(1),
  reasoning the protective order is not an injunction. The Court avoids vehicles
  where it might have to decide a jurisdictional question before reaching the one
  presented, and a denial here needs no explanation.
- **The "split" is thin.** The petition's circuit conflict is a list of circuits
  that honor party presentation against a handful of Fourth Circuit panels (and one
  Sixth Circuit dissent) said to depart from it. That is a pattern-of-error
  argument, not a doctrinal split, and the Court has just addressed the pattern in
  Margolin.
- **The panel's move is defensible as affirmance on the record.** The majority
  grounded its national-security interest in the district court's undisputed
  factual findings about danger to the Does' relatives in Afghanistan. An appellate
  court may affirm on any ground the record supports, so the Court may read this as
  a recharacterized interest rather than a new issue, which weakens the Margolin
  analogy (there the Fourth Circuit invented a jurisdictional theory).
- **Unattractive facts for a speech claimant.** The contempt finding concerned
  sharing a photograph of a seven-year-old adoptee, the Taliban has denounced the
  petitioner by name, and the order protects asylees with family still in
  Afghanistan. The Court is unlikely to want to loosen that order on an
  interlocutory record.
- **Waiver and no amici.** Respondents' waiver signals they see little risk, and no
  amicus has appeared on a petition that, if the First Amendment community thought
  it important, would have drawn some.

Net: a petition clearly above the baseline floor on quality and salience, held down
by posture and facts. I put P(any grant) at 0.11, with most of that mass on a GVR or
short per curiam rather than plenary review. `predicted_disposition` is `denied`.

## The other claims

- **relist-increment 0.35.** From one distribution, the increment fires if the
  Court calls for a response (which adds a later distribution) or relists. I weight
  the response request as the main path, around 0.25 on its own given the
  petition's quality and the First Amendment posture, with relists and
  reschedules adding the rest. The relist-count cut buckets by terminal count and
  cannot be read as a forward hazard, so this is judgment, not a looked-up row.
- **cvsg-increment 0.05.** Above the paid-segment CVSG share (about 1.2% of the
  cut) because the government's interest is the contested point and the United
  States never spoke to it, but a private protective-order dispute is not a
  usual CVSG candidate.
- **summary-disposition-route 0.6 (conditional on grant).** The petition itself
  invites a GVR in light of Margolin, the Court's recent corrections of the Fourth
  Circuit on this principle were summary, and the interlocutory record is a poor
  plenary vehicle. I keep this below the ~0.75 that a pure GVR-request petition
  would carry because the First Amendment framing gives some chance of argument if
  the Court takes it at all.
- **dissent-from-denial 0.08 (conditional on denial).** A sustained prior restraint
  is the kind of thing that occasionally draws a statement, but the facts and the
  jurisdictional dissent make silence the comfortable outcome.
- **big_case_score 0.45.** Decided, it would be a prominent decision because of the
  facts, but the legal holding would be about appellate procedure.

## Retrieval and its limits

- `fedcourts query` has no subject filter, so the corpus priors I pulled (recent
  SCOTUS grants in the 2020s era) were not topically comparable and did not move
  the number.
- CourtListener's docket index holds no rows for this petition (26-226) or for the
  companion petition No. 26-164 (A.A. v. Mast, from the Supreme Court of Virginia's
  adoption ruling), so I could not check whether anything post-dates the snapshot
  on either docket or whether the two are being considered together. CourtListener
  does confirm the Fourth Circuit opinion is published (Baby Doe v. Joshua Mast,
  No. 24-1900, filed April 22, 2026). The MCP server worked; the gap is coverage.
- I did not see this case's disposition anywhere, and the October 16 conference has
  not occurred as of the snapshot date.

## Where to discount me

The biggest uncertainty is how the Court reads the panel's footnote: as a genuine
party-presentation breach of the kind it corrected in Margolin (which would make a
GVR cheap and likely) or as an ordinary affirmance on record-supported grounds
(which makes this a routine denial). If the former, 0.11 is too low by a factor of
two. I also cannot see the companion adoption petition's status; if 26-164 is being
held or relisted, this docket may travel with it and the relist increment is too low.
