# Rationale for P(grant) = 0.015

## What the cell is

A forward, cert-stage cell at the distribution moment. `record/context.json`
freezes `band: baseline` under `sal-v4`, `distribution_count: 1`, no CVSG,
Term 2025, `signals_observable: true`. I read the provisioned snapshot
`2026-09-18.json`, `documents/petition.txt` (29 pages, text extracted, not
truncated), and `documents/questions-presented.txt`. There is no brief in
opposition: the respondent waived its response on June 22, 2026.

## Anchor

The statpack's "Segment base rate by salience band (sal-v4)" table matches
the context's salience version and carries a `baseline` column, so it is my
anchor. Pooling the bracketed `reached` figure for `baseline` over every
Term the table renders strictly before 2025 (Terms 2017–2024) gives
**5.1%** (weighted n = 11,580). That is the grant rate among paid petitions
that had reached the baseline band, which is this petition's position. For
shape only: the relist-count cut shows the never-relisted bucket resolving
at about 1.7% grant-family, and the CVSG cut shows "none" at about 6.3%.

## Adjustments down (the bulk of the move)

1. **Response waived and no call for a response as of the snapshot date.**
   The petition was distributed June 24 for the September 28 long
   conference. Twelve weeks have passed without a call for a response, and
   the conference is ten days away. The Court almost never grants a paid
   petition on a waiver without first requesting a response, so the grant
   path runs almost entirely through a last-minute call for a response
   (which I put near 5%) followed by a grant after the brief in opposition
   (perhaps 15–20% conditional). That alone puts the number near 1%.
2. **Forfeiture undercuts the split.** I read the Fifth Circuit opinion on
   CourtListener (published, unanimous panel of Judges Smith, Stewart and
   Ramirez, authored by Judge Smith). Footnote 7 says the D.C. Circuit
   "core customer" theory "appeared nowhere in plaintiff's second amended
   complaint and thereby was not ruled on by the district court and is
   forfeited on appeal." The petition frames the panel's refusal to engage
   that theory as the crystallized split; the panel's own ground was
   forfeiture plus non-bindingness. That is a vehicle defect the Court
   would see in the pool memo even without a brief in opposition.
3. **Fact-bound holding with alternative grounds.** The panel affirmed
   because Endure's own expert showed 27.7% of switching hospitals left the
   GPO model entirely and roughly 18–28% of purchases occur outside GPOs,
   because the Vizient-only market was a disfavored single-brand market
   with no lock-in evidence, and because Endure widened that market on
   appeal and failed to point to specific record evidence. Question 1 as
   framed asks whether "some" cross-shopping "must" defeat a submarket, but
   the panel did not adopt a per se rule; it weighed the plaintiff's own
   numbers under Rule 56.
4. **The asserted split is thin.** Whole Foods produced no majority
   rationale (two separate opinions and a Kavanaugh dissent), Newcal is a
   pleading-stage aftermarket case, and U.S. Sugar affirmed a *rejected*
   market. The petition's remaining authority is district-court merger
   cases. No circuit has squarely held that cross-shopping evidence is
   irrelevant at summary judgment.
5. **Private petitioner, low stakes signal.** A small relabeler against a
   GPO, a partly sealed record, a 20-page petition from a regional appellate
   firm, and a single amicus brief filed by a solo practitioner in her own
   name. Nothing in the amicus signal suggests an organized bar interest.

## Adjustments up (small)

The Fifth Circuit opinion is published and reasoned, market definition is a
recurring threshold issue, and the Court has shown some appetite for
antitrust doctrine in recent Terms. These keep me off the floor but do not
move the number much given the waiver and forfeiture points.

## The other claims

- `relist-increment` 0.10: routes are a call for a response before
  September 28 (about 5%), a hold or one-conference relist (about 4%), and
  a reschedule (1–2%). The statpack's relist cut buckets by terminal count
  and includes petitions with briefs in opposition, so I did not read a
  hazard off it directly.
- `cvsg-increment` 0.01: no federal interest, private parties, and the
  Court would call for a response first.
- `summary-disposition-route` 0.15: conditional on a grant, plenary review
  is the natural route; I know of no intervening decision on market
  definition for a GVR. I hold some mass for a hold-and-GVR on a case I am
  not tracking, which is why it is not lower.
- `dissent-from-denial` 0.02: the only Justice on record here argued the
  opposite direction from the petitioner.
- `big_case_score` 0.3: doctrinally consequential if decided, but a private,
  fact-bound dispute.

## Uncertainty and where to discount me

The largest uncertainty is whether a call for a response is already in
motion. The snapshot is stored as of today, and the CourtListener docket
record shows the case open with no filing since the July 16 amicus, but a
call for a response can issue any day before the conference. If one issues,
the number should roughly triple. I also have not seen the sealed appendix,
so the strength of the record evidence on distinct pricing and switching
costs is taken from the petition's own description and the panel's reading
of it.

## Retrieval health

The CourtListener MCP server was available and all calls succeeded. One
`fedcourts query` for recent SCOTUS priors returned only September 2026
emergency applications, ranked by recency, and gave me no comparable cert
priors; I relied on the statpack for base rates instead.
