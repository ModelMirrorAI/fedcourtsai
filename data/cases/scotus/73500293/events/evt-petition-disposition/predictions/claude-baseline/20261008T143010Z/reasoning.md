# Rationale for the numbers

**P(grant) = 0.30; predicted disposition: denied.**

## What I read

Provisioned inputs: the snapshot `2026-10-08.json` (the docket of No. 25-1391 through September 30, 2026), `context.json` (forward mode, band `baseline` under sal-v4, distribution_count 1, no CVSG, Term 2025, paid), `event.yaml` (cert stage, moment: distribution), and the three provisioned documents listed in `documents.json`: `questions-presented.txt`, `petition.txt` (162 pages, text truncated, which cut the appendix rather than the argument), and `brief-in-opposition.txt` (48 pages, full). Beyond those, in forward mode I fetched the petitioners' reply brief from supremecourt.gov (it was docketed September 30, before the snapshot, but not provisioned) and confirmed through the CourtListener MCP server that the Fifth Circuit opinion (Vetter v. Resnik, No. 25-30108, Jan. 12, 2026) is a published opinion. See `retrieval.md`.

## Anchor

The context carries band `baseline` under sal-v4, which matches the statpack's "Segment base rate by salience band (sal-v4)" table. The bracketed `reached` figure for `baseline`, pooled over the eight Term rows strictly before OT2025 that the table renders (OT2017 through OT2024, n roughly 11,600 weighted), is about 5 percent (per-Term 4.5 to 5.9 percent). That is the scored yardstick and my starting point. Cross-checks: the relist-count cut gives a petition that ends at zero relists a 1.2 percent grant rate and one at one relist about 13 percent (grant plus GVR); the CVSG cut gives about 35 percent grant-family conditional on a CVSG; the Fifth Circuit's originating-circuit rate is about 3.7 percent grant-family. The modern discretionary-cert base rate overall is a few percent.

The band is `baseline` because sal-v4 keys on docket trajectory and caption class, and this petition has had one distribution, no CVSG, and private parties. The band does not see what is unusual about this petition, which is why I move a long way from the anchor.

## Adjustments upward (large)

1. **Counsel and amici.** Paul Clement for petitioners; E. Joshua Rosenkranz for respondents; Lisa Blatt for an amicus. Five cert-stage amicus briefs, including the Motion Picture Association, RIAA/NMPA/A2IM, Paramount, IFPI and other international federations, and more than twenty copyright scholars. Cert-stage amicus volume at this level and repeat-player counsel on both sides are among the strongest observable grant correlates, and the statpack publishes no cut for them, so the adjustment is judgment rather than a table.
2. **The decision below.** A published Fifth Circuit opinion that, by the BIO's own account, is the first appellate decision on the geographic scope of section 304(c) termination, and that departs from the position of Nimmer, Patry, Goldstein, the Copyright Office's drafting history, and the one prior district court holding (Siegel). The Court does take "first circuit to decide, but wrong and consequential" copyright cases without a split when the practical stakes are national (its copyright docket is small but not split-dependent).
3. **Federal and international dimension.** The limiting text came from the Copyright Office; the petition presses Berne national-treatment and section 104(c); the reply invites a CVSG. This raises both the CVSG probability and, through it, the eventual grant probability, since an SG brief supporting the petitioners' textual reading is plausible.
4. **Stakes.** Worldwide rights in catalogs being negotiated now for terms running decades; the petition gives a concrete licensing dispute (ABC and *Moonlighting*) and the BIO does not really dispute that the industry is adjusting to the ruling, which the reply turns into evidence of disruption.

## Adjustments downward (substantial)

1. **No circuit split.** The BIO's lead point is correct: only one circuit has decided the question, the Second Circuit's *Fred Ahlert* language is not a holding, and the only contrary authority is a 2008 district court ruling later reversed on other grounds. The Court's modal response to a well-lawyered single-circuit petition is still denial for percolation.
2. **Vehicle.** The Fifth Circuit separately held that Vetter owns worldwide the renewal half he bought from the co-author's heirs, and the petition does not squarely challenge that holding. The BIO argues petitioners could obtain only co-ownership of foreign rights even if they win. The reply answers that the renewal holding rests on the same "foreign rights travel with U.S. rights" logic and is subsumed in the question presented as written ("authors or their heirs ... by operation of U.S. law"). That answer is plausible but not airtight; some Justices will see a manufactured vehicle (petitioners bought the Resnik interest after the mandate to bring this petition).
3. **Posture.** A test case built by respondents' counsel, from the Middle District of Louisiana, on a 1963 grant of one song. The Court sometimes prefers to wait for a cleaner, higher-value dispute from the Second or Ninth Circuit, which the BIO argues is where follow-on suits will arise.

## Decomposition

P(CVSG) about 0.33. P(grant | CVSG) about 0.45 (the SG is more likely than not to side with the Copyright Office's reading, but could flag the vehicle problem). P(grant | no CVSG) about 0.22 (a direct grant after one or two relists, versus denial after the Court takes a closer look). Combined, about 0.30. Because P(grant) is below 0.5, `granted` is 0 and the predicted disposition is `denied`.

**relist-increment 0.62.** Any CVSG produces a later redistribution (counted); any grant almost certainly follows at least one relist; and a petition of this profile is relisted before denial perhaps 30 percent of the time. 0.33 + 0.67 × (0.22 × 0.95 + 0.78 × 0.30) is about 0.63.

**cvsg-increment 0.33.** As above. Against it: the Court often grants or denies prominent private copyright petitions without inviting the SG, and a CVSG here delays a question the petition says is urgent.

**summary-disposition-route 0.03** (conditional on grant). No intervening decision; a reasoned published opinion; summary reversal of a first-impression statutory holding is very unlikely.

**dissent-from-denial 0.08** (conditional on denial). Commercial statutory question; a statement respecting denial noting importance and percolation is conceivable but uncommon.

**big_case_score 0.45.** High within copyright and the entertainment industries, with treaty and comity angles, but a technical ownership question with limited salience outside them.

## Uncertainty and where to discount me

- The largest uncertainty is how heavily the Court weighs the absence of a split against the amicus-backed importance showing. Reasonable forecasters would put this anywhere from 0.15 to 0.45.
- I have no statpack cut for amicus count or counsel quality; those adjustments are judgment.
- The BIO's statement of the case (its account of the renewal-half transaction) I skimmed rather than read in full; my read of the vehicle issue rests on the BIO's argument section and the reply's response.
- The petition text was truncated at 162 pages, but the cut fell in the appendix; the full argument was readable.
- The reply brief was retrieved outside the provisioned set (disclosed in `flags.json`). It is a pre-decision filing and raises no leakage concern in forward mode, but a predictor working from the provisioned set alone would not have seen the CVSG invitation or the "subsumed" answer to the vehicle argument.
- The corpus query I ran returned generic recent grants (no subject filter exists for SCOTUS rows) and did not shape the number.
- I do not know this case's outcome; the docket shows nothing after the September 30 distribution and the conference is October 16, 2026.
