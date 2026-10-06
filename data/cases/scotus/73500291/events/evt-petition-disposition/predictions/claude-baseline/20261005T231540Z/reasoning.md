# Reasoning — Hershey v. City of Bossier City, No. 25-1389

**P(grant family) = 0.24; predicted disposition: denied.**

## Anchor

`record/context.json` freezes `band: elevated` under `sal-v4`,
`distribution_count: 2`, `cvsg_date: null`, `term: 2025`, mode `forward`. The
statpack's "Segment base rate by salience band (sal-v4)" table matches the
context's salience version, so the anchor is the `elevated` column's bracketed
`reached` rate pooled over the Term rows strictly before 2025 that the table
renders (2017–2024, eight rows): **17.2% (n = 2810)**. Two cross-checks sit
beside it: the relist-count cut's bucket for one relist (the docket's two
distributions, one true relist — no "Rescheduled" entry between them) reads
granted 8.2% + gvr 5.1% ≈ 13% grant family; CA5 petitions overall run ~3.7%
grant family. Base rate read: `metrics/statpack.md` sections "Modern
discretionary-cert petitions by disposition", "by originating circuit", "by
relist count (paid scored segment)", "by CVSG status (paid scored segment)",
and the sal-v4 band table.

## What I read

The provisioned 2026-10-05 snapshot; `questions-presented.txt`; `petition.txt`
(223 pp., flagged truncated — the body and reasons sections are intact, the cut
falls in the appendix); `brief-in-opposition.txt` (41 pp., complete). No reply
brief text is provisioned (the Sept. 1 reply appears only as a docket entry).

## Adjustments up from the anchor

- **A real relist after the long conference.** The Oct. 5 redistribution for
  Oct. 9 follows actual consideration on Sept. 28; the many Sept. 28 petitions
  denied on Oct. 5 that `fedcourts query` returned confirm the Court was
  clearing that conference, and this one was carried over.
- **Fifteen cert-stage amicus briefs** (Cato, FIRE, Manhattan Institute, ACLJ,
  Buckeye, religious-liberty groups, members of Congress) — an unusually heavy
  showing that the band partly, but probably not fully, prices in.
- **Counsel on both sides.** Paul Clement with First Liberty for the
  petitioner; the City retained Jeffrey Wall (Gibson Dunn) for the BIO and has
  its own cross-petition (No. 25-1323). Both sides treating the case as
  cert-serious raises the odds the Court engages with the pair.
- **A Fifth Circuit intramural fight on the record.** Judge Ho's panel
  concurrence and en banc concurrence frame the question exactly as the
  petition does; Judge Oldham's seven-judge dissental and Judge Ho's dissent
  from panel rehearing give the Court a visible disagreement to resolve.

## Adjustments down

- **The BIO's vehicle argument is strong.** Hershey never cited Hope in the
  district court or the court of appeals; the question entered through Judge
  Ho's sua sponte concurrence; the out-of-time rehearing motion was denied.
  The Court's "pressed or passed upon" practice bites hard on a petition whose
  own question was first raised by a judge, and the BIO documents it from the
  CA5 briefs.
- **The premise is contested on its own terms.** Eight of the nine Fifth
  Circuit judges who wrote or joined opinions say Hope applies to First
  Amendment claims; the BIO cites post-Villarreal Fifth Circuit decisions
  applying obviousness to First Amendment claims (Wetherbe, Degenhardt). A
  merits case would have no party defending the rule the petition attacks.
- **The outcome would likely not change.** Judge Richman's concurrence rests on
  the unsettled forum status of arena grounds during a ticketed private event
  and on the thin viewpoint-discrimination allegation (no allegation the
  officers saw either leaflet). Even a win on the QP would leave a factbound
  obviousness fight on remand.
- **The Court passed last Term.** Cert was denied in Villarreal v. Alaniz
  (146 S. Ct. 939 (2026)) over Justice Sotomayor's dissent, and in Wetherbe
  (No. 25-530) — two recent chances to police the Fifth Circuit's First
  Amendment obviousness analysis that the Court declined.
- **No free-exercise claim was pleaded below**, so the religious-liberty
  framing that drew the amici is not cleanly in the case.
- **Plaintiff-side qualified-immunity grants are rare and usually summary**;
  the vehicle problems make a per curiam reversal harder to write here.

Net: I move from 17% to **0.24**. The relist, the amicus wall, and the paired
cross-petition pull up; the forfeiture and the Court's recent denials on the
same Fifth Circuit question pull down almost as hard. I would not be surprised
by a denial with a Sotomayor or Thomas writing, which is my modal outcome.

## Claim-by-claim

- `disposition` 0.24 — as above.
- `relist-increment` 0.45 — forecasting from two distributions. The paid
  scored segment shows roughly 28% of once-relisted petitions relisted again;
  I go above that because a separate writing on denial and coordination with
  the City's cross-petition are both live here.
- `cvsg-increment` 0.04 — no federal interest beyond the general one in
  qualified-immunity doctrine; CVSGs after a relist are rare.
- `summary-disposition-route` 0.3 — conditional on a grant: a Taylor v.
  Riojas-style per curiam is a real route for a Fifth Circuit
  qualified-immunity case, but the forfeiture and factbound forum question
  make plenary review (likely alongside No. 25-1323) the likelier grant shape.
  No intervening decision for a GVR.
- `dissent-from-denial` 0.4 — conditional on denial: the Villarreal dissent
  shows an engaged Justice on precisely this question, the relist is consistent
  with a writing in progress, and the religious-speech facts invite a statement.

## Big-case score

0.5. If decided, the ruling would be read across all Section 1983 litigation
and is backed by fifteen amici, but it would most likely reaffirm Hope rather
than announce a new rule, and the underlying dispute is one leafleting
encounter.

## Uncertainties and where to discount me

- I could not find the City's cross-petition (No. 25-1323) in the corpus
  (`open-events`) or on CourtListener, so I do not know whether it was
  distributed for Sept. 28 or Oct. 9 or relisted in tandem. If the relist
  here is mostly the Court waiting for the cross-petition to ripen, the relist
  signal is weaker than I have weighted it; if the City's petition was itself
  relisted, the pair is likelier to be granted together and my number is low.
- `fedcourts query` has no subject filter, so the priors it returned (recent
  grants and recent long-conference denials) informed only the reading of the
  Oct. 5 order list, not the qualified-immunity-specific odds.
- The petition's truncation falls in the appendix, so I read the Fifth
  Circuit opinions only as both briefs characterize them.
- The reply brief is not provisioned; whatever it says on forfeiture is unseen.
- Nothing I retrieved concerned this petition's own disposition; the case is
  pending for the Oct. 9, 2026 conference as of the snapshot.
