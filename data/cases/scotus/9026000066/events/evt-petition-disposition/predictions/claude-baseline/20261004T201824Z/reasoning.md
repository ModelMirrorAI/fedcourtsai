# Rationale for my numbers

**P(any grant) = 0.005; `predicted_disposition` = `denied`.**

## Anchor

`record/context.json` freezes `band: baseline` under `sal-v4`, one distribution, no CVSG, Term 2026, `forward` mode. The statpack's "Segment base rate by salience band (sal-v4)" matches that version, so the yardstick is the baseline band's bracketed `reached` rate pooled over Term rows strictly before 2026. Pooling 2017–2025 by their `n`:

| Pool | Rate | n |
| --- | --- | --- |
| baseline `reached`, 2017–2025 | 5.0% | 12,720 |
| baseline `ended` (leading figure), for contrast | 1.2% | 9,635 |

So the scored baseline is about 5% — the grant rate across every private paid petition that ever sat in the baseline band, counseled petitions with real splits included. Everything else I read moves this petition well below that pool's center.

## Adjustments down

- **Pro se paid petition.** The snapshot lists the petitioner as their own attorney and the petition is signed "Pro Se Petitioner". Within the paid segment, self-represented petitions grant at a small fraction of the counseled rate; the 5% pool is dominated by counseled filings.
- **Decision below.** An unpublished memorandum decision of the Arizona Court of Appeals, Division Two, affirming a dissolution decree, with the Arizona Supreme Court denying review. The statpack's originating-court cuts show state-court petitions granting far less often than circuit petitions (the `ariz` bucket in the circuit table is 30 of 30 denied; the state-court rows in the fuller table sit at zero to low single-digit grant rates). The salience class is private, so no caption-class uplift.
- **Questions presented.** I read `record/documents/questions-presented.txt` and `petition.txt` in full. All three questions are fact-bound grievances about how one Arizona panel handled waiver, harmlessness, and a missing-transcript presumption in one family-law appeal. The petition cites no conflict among lower courts, no decision of this Court the panel contradicted, and no recurring question beyond a general claim that family dockets are high-volume. Its strongest hook, the *Lee v. Kemna* inadequate-state-ground framing of Question 1, is a vehicle argument, not a reason to grant.
- **No respondent engagement.** The response was due August 14, 2026; the snapshot shows no brief in opposition, no waiver, and no call for a response, and the Clerk distributed the petition anyway on September 2. There is no provisioned `brief-in-opposition.txt`, consistent with nothing having been filed. A petition the Court does not ask the respondent to answer is one it has not flagged as worth a look.
- **No GVR hook.** The grant family's GVR share is substantial in most Terms, but a GVR needs an intervening decision bearing on the questions; none exists for these Arizona-procedure issues.

Together these put the petition in the bottom tail of the baseline pool. I land at 0.5%, roughly a tenth of the anchor. I did not go lower because the scoring rule is proper and some residual mass belongs on outcomes I cannot see (an intervening decision before disposition, an unexpected call for a response that changes the posture).

## The other claims

- **`relist-increment` 0.10.** The snapshot shows one distribution. In the baseline pool about 24% of petitions that reach the band leave it, which I read as the rate of acquiring at least one more distribution entry; that includes reschedules and counseled petitions a Justice holds. For a pro se, unopposed family-law petition at the long conference I take well under half of that. A reschedule or an unexpected call for a response is the main residual path.
- **`cvsg-increment` 0.002.** Private parties, state family-law procedure, no federal interest.
- **`summary-disposition-route` 0.6.** Conditional on any grant. The prior Terms' cert-order share of grants runs roughly 30–59% per the statpack's own note; for this petition a plenary grant is far less plausible than a summary route, so I shade above that range. The conditional is nearly moot given the grant number, but it is stated as a conditional, not a product.
- **`dissent-from-denial` 0.005.** Conditional on denial. Nothing here engages any Justice's standing concern, and pro se family-law denials essentially never draw a separate writing.

## Stakes

`big_case_score` 0.02: a private dissolution dispute between two former spouses, pro se, with no doctrinal reach.

## What I consulted and what I could not

I read the snapshot `2026-10-04.json`, `context.json`, `documents.json`, the petition, and the questions presented. One `fedcourts query` for recent denied SCOTUS priors returned mostly emergency applications ranked by recency and was not informative for a cert petition of this profile. Four CourtListener MCP searches (the Arizona memorandum decision by docket number and by content; the SCOTUS docket by number and by the petitioner's name) all returned zero results, so I had no view of the decision below beyond the petition's own characterization of it, and no docket state beyond the provisioned snapshot. The forecast rests on the provisioned inputs and the committed statpack.

## Where to discount me

The anchor is a segment-wide rate and my number is a strong downward adjustment from it on the basis of petitioner type and vehicle quality; if the harness's own cuts later show pro se paid petitions granting at a rate closer to the pool, I was too confident. My read of the decision below is entirely through the petitioner's account. The snapshot was created the day after the September 28 conference and carries no order, so the cell is correctly forward, but it will resolve within days of this run.
