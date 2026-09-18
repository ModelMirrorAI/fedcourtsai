# Rationale for the numbers

**P(grant) = 0.005; predicted disposition `denied`.**

## Anchor

`record/context.json` freezes `band: elevated` under `sal-v4`, `distribution_count: 2`, `cvsg_date: null`, `term: 2026`, forward mode, snapshot `2026-09-18.json`. The statpack's *Segment base rate by salience band (sal-v4)* table has an empty 2026 row, so I pooled the bracketed `reached` figures for `elevated` over the nine prior Terms it renders (OT2017–OT2025, n from 275 to 400 per Term; weighted denominator ≈ 3,085). The pooled reached rate is **≈ 17%** (range 13.5%–20.5% across Terms). That is the yardstick the evaluator will score this cell against, and I am deliberately far below it.

The corpus-wide vintage of the pack I read is the committed `metrics/statpack.md`; the snapshot itself carries the Court's `sJsonCreationDate` of 09/17/2026, one day before the snapshot date.

## Why I depart so far from the band anchor

1. **The band rests on a mis-read distribution count.** The two `DISTRIBUTED` entries are not two distributions of the petition. The March 19 filings were a *motion for leave to proceed as a veteran* (the docket says "Linked with 25M81", a miscellaneous motion docket) plus the petition; the May 19 distribution for the June 4 conference was of that motion, which the Court denied on June 8 ("Motion Denied."). The petition was then received August 6, docketed as paid No. 26-173, and distributed **once**, on August 26, for the September 28 long conference. Read correctly this is a relist-0 petition at its first conference, whose relist-count bucket in the paid scored segment grants ~1.2% (plus ~0.5% GVR), not an `elevated`-band petition. I am flagging this in `flags.json`; the band is still what I am scored against, but my probability should reflect the actual posture.

2. **The Solicitor General waived.** The respondent is a federal agency represented by the SG, who filed a waiver of the right to respond on August 19. When the Court is interested in a petition against the United States it requests a response before acting; a waived pro se petition that goes straight to the long conference is denied at a rate close to the paid-docket floor for private petitioners (the `baseline` band's bracketed reached rate is ~4–6%, and pro se filings sit well below that segment average).

3. **The petition is a poor vehicle on its own terms.** I read `questions-presented.txt` and the full `petition.txt` (49 pages, `empty_text: false`, not truncated). The petitioner is pro se. QP 1 asserts a circuit split on record-rule exceptions but supports it with a general ranking of circuits and one Ninth Circuit case (Lands Council v. Powell) against one D.C. Circuit case; the Fourth Circuit's own precedent (Casa de Maryland; National Veterans Legal Services Program) is cited as the petitioner's friend, so the "split" is at bottom a claim that the panel misapplied its own circuit's rule — an error-correction ask. QP 2 is compound and fact-bound (whether a commander's declaration conceded lack of jurisdiction). The petition mis-describes several authorities (State Farm v. Campbell is presented as a record-rule case; Loper Bright as governing record supplementation) and mixes in Fourth, Fifth, Sixth and Fourteenth Amendment and Double Jeopardy theories that were not the basis of decision below. The Fourth Circuit's decision is unpublished ("not yet reported"; the petition describes it as finding "no reversible error"), which the Court usually treats as a weak vehicle. No brief in opposition exists to weigh (`documents.json` lists only the petition and the QP cut; the respondent waived), so the "weigh the petition against the BIO" step is inapplicable rather than degraded.

4. **Originating circuit.** The `ca4` cut in the modern-cert-by-circuit table grants 1.3% (plus 1.2% GVR) — at the docket average, no adjustment either way.

Putting these together: a paid pro se petition at its first distribution, federal respondent waived, unpublished decision below, no genuine split. My honest probability of any grant (including GVR) is about half a percent. I round to **0.005** rather than lower because GVRs occasionally reach pro se petitions when an intervening decision bears on the case, and because the record-rule exceptions question is one some Justices have shown interest in abstractly.

## The other claims

- **relist-increment 0.07.** From the frozen count of 2, P(at least one more `DISTRIBUTED` entry). The main routes are a reschedule off the long conference (which adds an entry without a true relist) or a request for a response; both are uncommon for a waived pro se petition. The statpack's relist-count cut says most petitions never relist and the first relist barely raises the hazard of a second; from an effective relist-0 state at the long conference I put the forward hazard a little under 10%.
- **cvsg-increment 0.002.** The United States is the respondent; a CVSG is not called where the SG is already a party. Not zero only for clerical edge cases.
- **summary-disposition-route 0.65.** Conditional on a grant, P(disposed of in the cert order). The pack's overall modern-cert split is roughly 577 GVR to 655 granted (≈ 47% cert-order share among grants). For this case the conditional is higher: a grant of a pro se, unpublished-below APA petition would almost surely be a GVR, not plenary review. Stated as the conditional, not the product.
- **dissent-from-denial 0.01.** Conditional on denial. No clean question, no engaged respondent, unpublished below — separate writings on such denials are rare.
- **big_case_score 0.06.** Stakes are personal (one veteran's debarment from a DLA installation). The record-rule exceptions question is of modest general importance, but this petition would not be the vehicle that settles it.

## Uncertainty and where to discount me

- My biggest structural uncertainty is whether the harness's `distribution_count: 2` will also govern *resolution* of `relist-increment` (so a single further entry resolves it true) — I have stated the increment from the frozen count as the contract asks, regardless of my reading that one of those entries was not the petition's.
- I could not retrieve the Fourth Circuit opinion: two CourtListener MCP searches (docket 24-1166 in `ca4`; a party-name query) returned zero results, so my characterization of the decision below rests on the petition's own description and the docket's "not yet reported" marker. The MCP server responded normally; the opinion simply is not indexed.
- The one substantive `fedcourts query` I ran returned recent granted SCOTUS rows dominated by emergency applications and a state-court cert grant, none analogous to a pro se APA petition; it did not move the number. The first `query` attempt was rejected as a usage error (free-text argument) and read nothing.
- I know nothing about this case's outcome; the petition is pending for the September 28 conference.
