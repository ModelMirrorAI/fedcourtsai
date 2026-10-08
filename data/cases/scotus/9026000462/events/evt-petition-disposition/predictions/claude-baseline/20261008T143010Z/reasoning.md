# Rationale for the numbers

**P(grant) = 0.006; predicted disposition: denied.**

## Anchor

`record/context.json` freezes the cell as `forward`, `band: baseline` under `sal-v4`, Term 2026, `distribution_count: 1`, no CVSG. The statpack's "Segment base rate by salience band (sal-v4)" table is the matching version, so the anchor is the baseline band's bracketed `reached` rate pooled over the Term rows strictly before 2026 (OT2017–OT2025). Weighting each row's `reached` rate by its `n` gives roughly 637 grants over 12,720 petitions, about **5.0%** (range 3.9%–5.9% across the nine Terms). That is the yardstick skill is scored against, and it is the grant-family rate (plenary grants plus GVRs) for every paid private petition that ever reached the baseline band.

The relist cut (paid scored segment) reads: relist-0 petitions grant 1.2% (plus 0.5% GVR); relist-1 petitions grant 8.2% (plus 5.1% GVR). The CVSG cut: no CVSG, 4.0% granted plus 2.3% GVR. The Eighth Circuit's bucket in the originating-circuit cut: 1.2% granted, 1.4% GVR, 95.4% denied, which is slightly below the circuit average.

## Adjustments down from the anchor

The baseline band pools every paid private petition, from counseled petitions by repeat Supreme Court advocates down to this one. This petition sits at the very weakest end of that pool on every dimension I can read:

1. **Pro se petitioner.** The snapshot lists Ryan J. Hauber as his own attorney with no counsel of record; the district-court docket (CourtListener, N.D. Iowa 2:23-cv-01033) records every filing of his as "PRO SE". Pro se paid petitions grant at a small fraction of the counseled paid rate.
2. **Posture below.** The suit was an ADA employment claim (civil rights: jobs) against Honkamp Krueger & Co., an Iowa accounting firm. A magistrate judge recommended, and the district judge adopted on June 2, 2025, dismissal with prejudice as a Rule 37(b)(2) sanction for violating a discovery order, with a $500 monetary sanction; the trial was cancelled. The Eighth Circuit affirmed on March 23, 2026 (district-court docket entry: "We affirm"), and the appeal docket's `nature_of_suit` is blank; the opinion is not in CourtListener's opinion index, which is consistent with an unpublished per curiam. A discovery-sanction affirmance reviewed for abuse of discretion is fact-bound and carries no circuit split.
3. **Respondent waived** on the day the petition was docketed, and I expect no call for a response: the Court almost never grants without a response, and a request for one is itself unlikely here.
4. **Sealed supplemental appendix.** The petition rode in with a motion to file a supplemental appendix under seal, which the Court granted on Oct 5. That reflects sealed material in the record below, not a signal of merit.
5. **No intervening decision** of this Court would make a GVR the natural outcome.

Against those, nothing pushes up: the petitioner is a private individual, the respondent is a private firm, and the question (whatever its drafting) is an abuse-of-discretion sanctions review.

Taking the baseline anchor of about 5% as the population rate and placing this petition in its weakest decile, I put P(any grant, GVR included) at **0.006**. I would not go below roughly 0.003, because the band rate includes a GVR share and a stray GVR or a surprise is always possible; I would not go above about 0.015 on this record.

## The claims

- `disposition` 0.006, equal to the top-level probability.
- `relist-increment` 0.97. The frozen `distribution_count` of 1 is the Sep 9 distribution for the Sep 28 long conference, which carried the motion 26M22 (granted Oct 5), not the petition, which was docketed only on Oct 7 with a waiver filed the same day. The petition will therefore be distributed again, almost certainly in late October for an early-to-mid-November conference. The residual 0.03 covers a dismissal under Rule 46 or other termination before distribution, and the possibility that the harness's distribution reading counts that next entry differently from what I expect. This is a forecast about one more distribution, not a true relist in the sense of the statpack's cut; see the flag.
- `cvsg-increment` 0.002. Private employment dispute, no federal interest; CVSGs are vanishingly rare on pro se petitions.
- `summary-disposition-route` 0.75, conditional on a grant. If this petition were granted at all it would be by a summary order, not plenary review; I leave 0.25 for the possibility that the only path to a grant would be some unforeseen question the Court wanted argued.
- `dissent-from-denial` 0.01. Nothing about the case invites a statement respecting denial.

## Big-case score

0.03. A pro se discovery-sanction dismissal in a private ADA suit; no stakes beyond the parties.

## What I could and could not read

- `documents.json` shows the petition fetched (46 pages) with `empty_text: true`, so no text layer could be extracted and no `questions-presented.txt` exists. My read of the petition's questions is inference from the posture below, not from its text. No brief in opposition exists (the respondent waived).
- I read the Northern District of Iowa docket entries through the CourtListener MCP server to learn the posture; I could not retrieve the Eighth Circuit opinion itself (it does not appear in the opinion index). The district docket also shows post-judgment motions to reconsider denied on Aug 10, 2026, and a separate mandamus petition (CA8 No. 25-3033) denied Oct 21, 2025, neither of which changes the cert calculus.
- The corpus `query` calls returned recent granted and denied SCOTUS priors from the 2020s era for shape only; none is a close analogue and I did not weight any individual prior.
- Retrieval was unrestricted (forward mode). Nothing I retrieved disclosed this petition's disposition; the latest district-docket entry postdates the petition's filing but concerns the district court's own reconsideration ruling.

## Where to discount me

The main uncertainty is the exact level within a very low range: whether pro se paid petitions of this shape grant at 0.3% or 1%. The direction of the call is not in doubt. The relist-increment number is the one most sensitive to how the harness reads docket entries, since it turns on whether the next "DISTRIBUTED for Conference" line counts against the frozen count of 1.
