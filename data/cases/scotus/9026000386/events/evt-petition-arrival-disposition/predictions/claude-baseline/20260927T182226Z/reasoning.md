# Reasoning — why P(grant) = 0.005

## What this cell is

Arrival-moment cert cell, `forward` mode, salience version `sal-v4`, band
`baseline`, Term 2026, zero distributions, no CVSG. I read the provisioned
snapshot `2026-09-23.json` (one docket entry: petition filed, response due
October 22, 2026), `questions-presented.txt`, and `petition.txt` (23 pages,
full text, not truncated). No brief in opposition exists yet, as expected at
arrival.

## Anchor

The context's band is `baseline` and the caption is private (an individual
against a Michigan school district and state agency — the respondents are a
state, but the *petitioner* is private, and the class floors key on the
petitioner's caption class). The statpack's "Segment base rate by salience
band (sal-v4)" table matches the context's salience version, so I anchor on
`baseline`'s bracketed `reached` rate pooled over the rendered Terms strictly
before OT2026 (OT2017–OT2025, nine rows):

| pooled window | grants (weighted) | n (weighted) | reached rate |
| --- | --- | --- | --- |
| OT2017–OT2025 | 637 | 12,720 | 5.0% |

That 5.0% is the arrival population's own grant-family rate for private paid
petitioners (it includes GVRs). It is the yardstick the evaluator scores this
cell against, and it is a ten-fold-wide pool relative to where this petition
sits within it.

## Adjustments, all downward

1. **Pro se petitioner.** The petition is filed by the petitioner himself; the
   snapshot lists him as his own attorney and the petition is signed "pro se".
   Pro se paid petitions grant at a small fraction of the counseled paid rate;
   the `baseline` class pools both, and the counseled majority drives its 5%.
   This alone takes me most of the way from 5% to under 1%.
2. **No cognizable legal question.** The three questions presented are not
   questions of federal law the Court could resolve as written (see
   `predicted_reasoning.md`). The petition's argument section is largely a
   verbatim reproduction of Public Law 91-373 and a Michigan statute, plus a
   list of pro se-pleading-standard cases. There is no claimed circuit split,
   no conflicting state high-court decision, and no published opinion below.
3. **Posture below.** CourtListener confirms the E.D. Mich. case (1:24-cv-11604,
   Judge Parker) was a § 1983 suit alleging due process and CARES Act
   violations, dismissed on February 26, 2025 by adopting a magistrate judge's
   report: motions to dismiss and for summary judgment granted, and the
   complaint dismissed sua sponte against all defendants for failure to state
   any federal claim. The Sixth Circuit docket (No. 25-1514) shows a "judge
   order" and entry of judgment on April 1, 2026 and an order on June 24, 2026
   (rehearing denied), consistent with a short unpublished affirmance. A
   pleading-stage dismissal affirmed by unpublished order is the weakest
   vehicle the Court sees.
4. **Preemption theory is misdirected.** The petition's core claim is that
   Michigan's "reasonable assurance" denial provision conflicts with the 1970
   federal amendments. But the federal text the petition itself reproduces
   (§ 3309(b)(3), and the 1976 amendments it does not cite) *permits* states to
   deny between-terms benefits to non-professional school employees; Michigan's
   MCL 421.27(i) tracks that federal permission. There is no plausible conflict
   for the Court to resolve.
5. **No GVR vehicle.** The `summary-disposition-route` share of any grant is
   high only because a plenary grant is even less plausible; no pending or
   recent decision of the Court bears on the case, so the GVR channel is
   nominal.

I do not adjust upward for anything. The paid fee status is already priced
into the band table (it is the paid scored segment). The involvement of a
state and its agency as *respondents* does not move a private petitioner into
the `state` class.

## Result

P(grant) = 0.005. This is roughly a tenth of the 5.0% anchor. I considered
0.002–0.01; I settle at 0.005 because pro se paid petitions do occasionally
draw a GVR when a lead case lands, and I cannot exclude that channel entirely,
but nothing on this docket points to one.

## The other claims

- `relist-increment` 0.95: P(at least one distribution). This is the
  probability the petition is *not* dismissed or withdrawn before ever reaching
  a conference. A docketed paid petition is almost always distributed once; the
  residual is a Rule 14/Rule 33 defect dismissal or a withdrawal, which is rare
  but not negligible for a pro se filer.
- `cvsg-increment` 0.002: no federal interest and no plausible trigger.
- `summary-disposition-route` 0.85: conditional on a grant, almost the only
  route is a GVR. I leave 15% for a reformulated plenary grant because the
  conditional is being evaluated on a near-empty event and I hold little
  structure over it.
- `dissent-from-denial` 0.01: no signal.

## Uncertainties and where to discount me

- I have not seen the Sixth Circuit's order text (CourtListener holds only the
  docket entries, not the document), so "unpublished affirmance" is an
  inference from the docket shape and the petition's appendix listing.
- The `baseline` anchor is a population-wide number for private petitioners; my
  intra-class adjustment for pro se status rests on general knowledge of the
  cert docket rather than a published statpack cut, which does not split the
  paid segment by counsel status. If the pro se share of `baseline` grants is
  larger than I believe, I am too low.
- The corpus `query` calls returned recent emergency-application rows, not cert
  petitions comparable to this one, so retrieval of structured priors
  contributed nothing beyond the statpack.
- Forward retrieval: I read this case's own district-court opinion and
  appellate docket entries on CourtListener. Both predate the petition and are
  legitimate forward signal; I did not seek and did not find any disposition of
  the petition itself.
