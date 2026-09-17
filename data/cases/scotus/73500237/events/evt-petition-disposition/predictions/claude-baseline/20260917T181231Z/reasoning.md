# Rationale for the numbers

**P(grant) = 0.012.** Anchor first, then adjust.

## Anchor

`record/context.json` freezes `band: baseline` under `salience_version:
sal-v4`, `distribution_count: 1`, no CVSG, Term 2025, mode `forward`. The
statpack's "Segment base rate by salience band (sal-v4)" table matches the
frozen version, so the band is a valid anchor. Pooling the bracketed
`reached` figure for `baseline` over the Term rows strictly before OT2025
(OT2017 through OT2024, all eight rendered) gives roughly **5.1%**
(weighted n about 11,600). That is the rate faced by a paid, privately
captioned petition that has reached the baseline band, and the yardstick the
evaluator scores this cell against. For shape I also read the modern-cert
disposition table (grant family a few percent), the CA4 circuit cut (grant
1.3%, gvr 1.2%), the relist cut (relist-0 bucket: granted 1.2%, gvr 0.5%),
and the CVSG cut (no CVSG: granted 4.0%, gvr 2.3%).

## Adjustments downward (the bulk of the move)

1. **The Solicitor General waived a response** (docket entry of June 17,
   2026). The government waives when it sees no realistic prospect of a
   grant, and the Court almost never grants a petition on which the SG has
   waived without first calling for a response. No call for a response has
   issued in the roughly three months since the waiver, and the petition
   went straight to the long-conference distribution. This alone puts the
   petition well below the band's average.
2. **Vehicle problems on the face of the opinion below.** The Fourth Circuit
   (Wilkinson, J., joined by King and Gregory, JJ., published, 168 F.4th
   203) affirmed a Rule 12(b)(6) dismissal on two grounds: first, that
   Redding's own complaint conceded she could not perform the essential
   functions of the position she sought (so she is not a "qualified
   individual"), and second, in the alternative, that TSA in fact provided a
   reasonable accommodation via the FLETC reassignment she self-selected.
   The first ground is independent of every question presented; a grant on
   the interactive-process question would not change the judgment. The
   panel was unanimous and ideologically mixed.
3. **The split is asserted at a level the decision below did not reach.**
   The petition frames the well-known disagreement over whether a bad-faith
   interactive process is independently actionable (3d/5th/7th versus
   9th/10th/11th Circuits). But the Fourth Circuit did not adopt the
   "evidence only" side of that split; it held the accommodation actually
   provided was reasonable and the plaintiff not qualified. The petition's
   A.J.T. argument is that A.J.T. left the standards question open, which
   is a reason a future case might be granted, not a conflict with this one.
4. **QP III (Bumper v. North Carolina consent doctrine applied to an
   employment accommodation)** has no support in any circuit and signals to
   the Court that the petition is not a disciplined vehicle. The petition
   also has drafting lapses (a garbled QP I, a stray Fourth Amendment
   provision in the "provisions involved" section, an appendix caption that
   does not match the petition caption).
5. **Counsel profile.** Petitioner is represented by a small firm with no
   evident Supreme Court cert practice; the corpus pull of granted 2020s
   petitions shows the usual profile of elite appellate counsel and SG
   participation on the merits side, which this petition lacks.

## Adjustments upward (small)

- The underlying "dual-track" problem (agency simultaneously certifying to
  OPM that accommodation is impossible while offering a reassignment that
  extinguishes the retirement application) is a genuine and recurring
  federal-employment issue, and the petition documents an admission by the
  agency that the employee was not counseled. A Justice interested in the
  A.J.T. standards question could conceivably see something here.
- It is a paid petition from a published circuit opinion, which is the
  population the band table describes, so I do not discount further for fee
  class.

Net: roughly one-quarter of the band anchor. I set 0.012 rather than lower
because the anchor population already contains many weak petitions and a
call for a response remains possible in principle.

## Claim-level numbers

- `disposition` 0.012: equals the top-level probability.
- `relist-increment` 0.15: from one distribution for the long conference.
  Most such petitions are disposed of in one pass. The increment comes
  mostly from a possible call for a response (which produces a later
  redistribution) plus ordinary reschedules; the relist cut in the statpack
  shows a terminal relist-1+ share around a quarter of the paid scored
  segment, but that segment over-represents petitions the Court took
  seriously, and a waived-response petition sits below it.
- `cvsg-increment` 0.01: the Solicitor General is counsel for the
  respondent, so a CVSG is structurally near-impossible; I leave a sliver
  for docket irregularities.
- `summary-disposition-route` 0.25 (conditional on grant): no intervening
  decision supports a GVR, so a plenary grant is the likelier route
  conditional on any grant; I keep weight on a summary route because grants
  of low-profile petitions against the government sometimes resolve in the
  cert order.
- `dissent-from-denial` 0.03 (conditional on denial): well below the typical
  rate for baseline-band petitions with a plausible ideological hook, since
  the two independent grounds below make this a poor writing vehicle.

## big_case_score = 0.10

Stakes if decided: a narrow federal-employment Rehabilitation Act question
that would matter to federal employees pursuing disability retirement and
accommodation in parallel, but not beyond. Scored on stakes, not odds.

## Inputs used and their limits

- Snapshot `record/snapshots/2026-09-17.json` (three docket entries:
  petition filed May 28, 2026; federal respondents' waiver June 17, 2026;
  distributed June 24, 2026 for the conference of 9/28/2026).
- `record/documents/questions-presented.txt` and `petition.txt` (67 pages,
  full text, including the Fourth Circuit opinion in Appendix A). No
  brief in opposition exists because the respondent waived; my read of the
  government's position is inferred from the waiver and the opinion below,
  not from any filing.
- `metrics/statpack.md` sections named above.
- Retrieval: one `fedcourts query` for granted 2020s SCOTUS priors (shape
  only), and two CourtListener MCP docket searches, both returning zero
  results (CourtListener carries no docket record for 25-1336 and no
  pending SCOTUS docket matching the interactive-process query). I did not
  find and did not seek this case's disposition; the snapshot is dated
  today and the conference has not yet occurred.

## Where to discount me

I have not read the district court opinion or the joint appendix, so I take
the petition's account of the agency's concealment at face value while
noting the panel did not engage with it. If the Court is looking for a
vehicle on the A.J.T. standards question and is willing to overlook the
qualified-individual ground, my number is too low; a call for a response
would be the first visible sign of that.
