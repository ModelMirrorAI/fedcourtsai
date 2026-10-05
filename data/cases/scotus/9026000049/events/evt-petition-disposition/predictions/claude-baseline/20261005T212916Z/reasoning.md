# Why 0.38

## What I read

Provisioned inputs: `record/snapshots/2026-10-05.json` (the baseline; 16 docket entries through the 10/5 re-distribution), `record/context.json` (mode `forward`, band `state` under `sal-v4`, `distribution_count` 2, no CVSG, Term 2026, no cutoff), and all three provisioned documents: `questions-presented.txt`, `petition.txt` (182 pages, truncated, but the full body through the conclusion is present; only the appendix is cut), and `brief-in-opposition.txt` (48 pages, complete). Neither document was flagged `empty_text`. The reply brief is on the docket (Aug 26) but was not provisioned and I did not fetch it.

## Anchor

Cert-stage cell, moment `distribution`, band `state` frozen at prediction, salience version `sal-v4`, which matches the statpack's "Segment base rate by salience band (sal-v4)" table. Pooling the bracketed `reached` figure for `state` over every rendered Term strictly before OT2026 (OT2017 through OT2025, nine rows, weighted n = 419) gives a grant-family rate of about **23.6%**. That is my anchor. For shape only: the relist-count cut's bucket 2 shows a 41% grant family, but that bucket is the wrong read for this docket, because its two distribution entries are a reschedule before any conference plus the re-distribution, so the petition is really at zero considered conferences. The CVSG cut does not apply (none on the docket). The originating-circuit cut (CA8, 2.6% grant family) is slightly below the docket-wide rate but is dominated by the band.

## Adjustments up (from 24% toward 38%)

- **Amicus support is exceptional for a cert petition.** Six amicus briefs on the docket, including Oklahoma, Florida and 23 other States, and Senators Cruz and Grassley. A 25-State brief is one of the strongest cert-stage signals short of a CVSG.
- **The question is genuinely recurring and the Court will have to face it.** Four States (Texas, Oklahoma, Florida, Iowa) have illegal-reentry crimes; Iowa, Oklahoma and Florida's are enjoined while Texas's is enforceable only because the Fifth Circuit en banc dismissed the challengers on standing (United States v. Texas, No. 24-50149, April 24, 2026, which I read on CourtListener: it vacated the injunction without reaching preemption). The petition's "odd safe harbor outside Texas" framing is a real asymmetry.
- **The United States is on Iowa's side.** It supported rehearing en banc as amicus and dismissed its own suit. A CVSG, if issued, would almost certainly return a recommendation to grant, and the Court knows that.
- **Receptive bench.** The Kansas v. Garcia majority (five Justices) rejected preemption from "federal enforcement priorities," and Justice Thomas's concurrence there attacked obstacle preemption outright. The petition is built on Garcia and on the Salerno / NetChoice facial-challenge line, both current favorites. The Stras dissental (joined in part by Loken) gives the Court an opinion to adopt.
- **Interlocutory posture is a weak objection here.** Arizona v. United States was itself review of a preliminary injunction, and the petition notes the district court stayed proceedings pending this petition.

## Adjustments down (why not higher)

- **No merits circuit split, and the BIO says so credibly.** Every court to reach the merits of a state entry/reentry crime has found preemption; the Fifth Circuit en banc ducked the merits. The Court generally waits for a conflict, and here there are two live appeals (Padres Unidos v. Drummond, 10th Cir., argued March 2026; Florida Immigrant Coalition v. Attorney General, 11th Cir., argued October 2025) that could create one. I could not find either decided on CourtListener as of today. Percolation is the single strongest reason to deny or to hold off.
- **QP1 is a poor vehicle.** The BIO's point that MMJ member David has no lawful status and so has standing even under Iowa's reading is close to dispositive of the standing question's cert-worthiness, and Iowa's disavowal rests on a reading of SF2340 that the court below called counter-textual. I treat QP1 as adding little to grant likelihood.
- **The Court declined to let Florida's law take effect.** Uthmeier v. Florida Immigrant Coalition, 145 S. Ct. 2872 (2025) (stay denied), cited in the BIO. A stay denial is a different standard, but it is a data point that the Court was not eager to disturb the status quo on these laws in 2025.
- **Rescheduled before the first conference.** Rescheduling is weaker than a relist and often reflects a chambers wanting more time or a pairing with another matter; it is not evidence of four votes.
- **The respondents' brief is strong on the merits** and frames the panel's reasoning as faithful to Arizona and Crosby; the panel was unanimous and rehearing drew only one full dissent.

Net: roughly 24% anchor, pushed up by the amicus and federalism signals and pulled back by percolation and vehicle issues, lands at **0.38**. Because that is below 0.5, `granted` is 0 and `predicted_disposition` is `denied`, but I would not be surprised by a grant.

## The other claims

- `relist-increment` 0.55: see the forecast document. From a state of two distributions and zero considerations, a further distribution follows from a grant (near-certain), a CVSG (certain), or a dissent from denial (likely), and about a third of plain denials in this posture still pick up one relist.
- `cvsg-increment` 0.25: preemption question, United States absent as a party but with a stated interest. The government's view is already public, which cuts against the Court spending five months to get it in writing.
- `summary-disposition-route` 0.06 (conditional on grant): no intervening decision; a plenary grant is the only realistic grant route.
- `dissent-from-denial` 0.28 (conditional on denial): Thomas / Alito / Gorsuch have shown appetite on this doctrine, but a percolation-driven denial would most likely be silent.

## Where to discount me

- I did not retrieve the reply brief or the amicus briefs' contents; the amicus signal is counted from the docket entries alone.
- The Tenth and Eleventh Circuit statuses are from the petition (July 2026) and the BIO (August 2026) plus a CourtListener search that returned nothing; if either circuit has ruled since, the percolation calculus changes and this number is stale.
- I could not verify whether a cert petition from the Fifth Circuit's en banc Texas decision is pending; if one is, the reschedule may mean the Court is pairing the two, which would raise both the relist and grant probabilities.
- Corpus retrieval (`fedcourts query`) returned recent granted SCOTUS priors but offers no subject filter that isolates immigration-preemption petitions, so the priors it returned did not shape the number.
