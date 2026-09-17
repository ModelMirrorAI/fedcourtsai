# Why these numbers

**P(grant) = 0.004; predicted disposition: denied.**

## What I read

- `record/context.json`: forward mode, band `baseline` under `sal-v4`, one
  distribution, no CVSG, Term 2025, `signals_observable: true`.
- `record/snapshots/2026-09-16.json`: paid docket No. 25-1296. Petitioner Samuel
  Collin Robinson, pro se (he is listed as his own attorney, not counsel of
  record). Respondent Katherine Lyman Freeman. Lower court: Colorado Court of
  Appeals, No. 25CA0306, decided August 14, 2025; Colorado Supreme Court denied
  review November 24, 2025. Petition entry dated February 14, 2026 (docketed May
  20, 2026, so the filing was apparently held or corrected for about three
  months); response due June 22, 2026; no response, no waiver entry, no amicus.
  Distributed July 8, 2026 for the September 28, 2026 conference.
- `record/documents/petition.txt` (23 pages, text extracted, not truncated). No
  `questions-presented.txt` was provisioned; I cut the questions from the
  petition's "Questions to Review" section myself. No brief in opposition was
  provisioned, consistent with the docket showing none filed.
- `metrics/statpack.md`: the modern-cert base rate, the relist and CVSG cuts, and
  the sal-v4 segment table.

## Anchor

The context's `salience_version` (`sal-v4`) matches the segment table's heading,
and `baseline` is a rendered column, so the table is a valid anchor. Pooling the
bracketed `reached` figures for `baseline` over the Terms strictly before 2025
that the table renders (OT2017 through OT2024, weighted by their `n`) gives about
**5.1%** (roughly 593 grant-family outcomes over 11,580 weighted petitions).
That is the grant rate among paid private petitions that had reached the
baseline band, which is this petition's situation.

## Adjustments from the anchor, all downward

1. **Pro se petitioner, no counsel.** The paid scored segment's 5.1% is
   dominated by counselled petitions. Pro se paid petitions are granted only in
   the rare case of a clean, well-documented split, and this is not one.
2. **The federal question is a facial vagueness attack on the universal
   best-interests standard.** No court has accepted it, the petition cites no
   split (its authorities are Meyer, Kolender and Dimaya), and the Court has never
   suggested the civil best-interests standard is void for vagueness. The
   petition's "similar law prevails in all 50 states" point cuts against a grant:
   it means no conflict exists.
3. **Vehicle defects.** The judgment below rests on a state procedural rule
   (C.R.C.P. 7(b)(1) particularity), which is an adequate and independent state
   ground. The Colorado Court of Appeals also found the constitutional argument
   undeveloped and unsupported by authority, a preservation and development
   problem. The elder child aged out during the litigation, so half the
   controversy is moot. The decision below is unpublished.
4. **Repeat petitioner, same dispute.** The petition itself records that the same
   petitioner's earlier petitions from this custody case (Nos. 19-356 and 23-1244)
   were denied. A third petition on the same family's parenting plan has no
   better claim on the Court's attention.
5. **No response on file and no call for one.** The Court will not grant without a
   response; a CFR would have to come first, and nothing here invites one.

Each factor alone would push the number well under the anchor; together they put
it near the floor of what a live petition can honestly be given. I settled on
0.004 rather than something even smaller because a positive probability must
cover clerical or bulk-order surprises, and because a proper scoring rule
penalises overconfidence at the tails.

## Other claims

- **relist-increment 0.07.** The statpack's relist cut shows most paid scored
  petitions end at one distribution. From a single long-conference distribution
  with no response, I expect a denial on the first order list. The residual
  covers a bulk reschedule (which adds a distribution entry under the `dist-v2`
  reading even without a merits relist) and the small chance a Justice holds it
  briefly.
- **cvsg-increment 0.002.** No federal interest at all.
- **summary-disposition-route 0.35 (conditional on grant).** The grant-family
  split in the modern-cert section is roughly half GVR, but a GVR needs an
  intervening decision and none exists on this question; if the Court somehow
  granted, plenary review is likelier than a cert-order disposition. I keep the
  number above zero because a conditional on an event this unlikely is
  dominated by scenarios I cannot foresee.
- **dissent-from-denial 0.01 (conditional on denial).** Pro se family-law
  petitions essentially never draw a noted dissent or statement; the two prior
  petitions in this dispute drew none.

## Stakes

`big_case_score` 0.12. The stated question would be a landmark if the Court ever
decided it, but this case would decide nothing: a denial of a pro se petition
with no response and no coverage.

## Uncertainty and where to discount me

- I did not read the Colorado Court of Appeals opinion itself (only the
  petition's account of it), so my adequate-state-ground reading rests on the
  petitioner's own description of the particularity ruling.
- The three-month gap between the petition's file stamp and docketing is
  unexplained in the record; it does not change the forecast.
- The `fedcourts query` I ran returned recent emergency applications ranked by
  recency, not comparable pro se cert petitions, so it contributed nothing to
  the number; the corpus filters cannot target this petition's profile.
- CourtListener's docket index returned no rows for Nos. 19-356 or 23-1244 or
  for the petitioner's name, so the prior-petition history is taken from the
  petition's own statement, not independently confirmed.
- I do not know this case's outcome; the conference has not yet occurred as of
  the snapshot date.
