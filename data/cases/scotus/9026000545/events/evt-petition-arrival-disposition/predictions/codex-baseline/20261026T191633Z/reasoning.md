# Basis for the prediction

**P(any grant) = 0.006; predicted disposition: denied.** This is a cert-stage
arrival forecast, not a forecast of who should prevail on the employment
claims. The grant probability includes plenary grants, GVRs, summary reversals,
and partial grants.

## Information set

I used the event definition, `record/context.json`, the provisioned snapshot
`record/snapshots/2026-10-27.json`, `documents.json`,
`questions-presented.txt`, `petition.txt`, and the lower-court opinions and
orders reproduced in `appendix.txt`. The snapshot's sole proceeding is the
October 21, 2026 petition filing, with a November 25 response deadline; the
docketing date is October 26. The next-day snapshot filename and exclusive
October 27 cutoff bound that baseline; they are not evidence of a proceeding
after the run date. The frozen conditioning is forward mode, Term 2026,
sal-v4 baseline, zero distributions, and no CVSG. At arrival these missing
procedural signals are expected, not a defect or evidence that the case will
never acquire them.

Both substantive filings have extractable text and are marked untruncated and
not OCR-derived. No brief in opposition was provisioned, and I do not infer
what the respondent will argue. I read the actual appellate opinion in the
appendix rather than treating the petition's characterizations as holdings.
No outcome or subsequent history of this Supreme Court petition was sought,
encountered, or already known to me.

## Base-rate anchor

The petitioner is a private individual, notwithstanding the governmental
respondent. The correct arrival anchor is therefore the private class's
sal-v4 **baseline reached** rate, not the terminal baseline rate or the
terminal relist-zero bucket. The committed `metrics/statpack.md` displays ten
Terms, 2017–2026. Pooling every displayed Term strictly before 2026 and using
the corresponding exact `prefix_weighted_resolved` and
`prefix_est_grant_rate` values in `metrics/statpack.json` gives **659 grant-family
outcomes / 12,912 weighted resolved petitions = 5.104%** for Terms 2017–2025.
I executed that calculation locally. These are committed-pack estimates,
not a newly refreshed live-corpus measurement; no corpus service was queried.

For scale, the modern discretionary-cert section records 688 grants plus
589 GVRs among 44,786 weighted resolved petitions, about 2.85%, but that
whole-docket population includes IFP petitions and is not this paid private
arrival's anchor. The originating-circuit table also does not override the
class-specific anchor.

The paid-segment relist cut has 10,201 resolved in bucket zero, 2,538 in
bucket one, 495 in bucket two, and 484 in bucket three-plus. These terminal
buckets show that repeat consideration is a minority path, not the forward
hazard from this cell's zero distributions. The paid CVSG cut has 164 resolved
CVSG cases versus 13,554 without one; the CVSG bucket's grant-family rate is
34.8%, versus 6.4% without one. Those are terminal, all-Term descriptive
cuts, not as-at-arrival probabilities. The pack has no paid-segment
amicus-count cut; this snapshot names no amicus filing, and I make no
quantitative amicus adjustment.

## Why I move below the anchor

1. **The first alleged split is overstated as applied to this judgment.**
   The petition's first question and reasons section challenge the Eleventh
   Circuit comparator standard. But the appended June 8 appellate opinion,
   pages 6–8 (App. 9(a)–11(a)), expressly allows multiple forms of
   circumstantial evidence, then separately considers comparator evidence
   and pretext. It does not hold that every plaintiff must identify a
   comparator. The petition's equation of material similarity with near
   identity is also undermined by the antecedent en banc decision: *Lewis v.
   City of Union City*, 918 F.3d 1213 (11th Cir. 2019), retrieved through
   CourtListener, rejects the earlier near-identity formulation. Differences
   between circuits may still matter in other vehicles, but this petition
   does not demonstrate an outcome-determinative conflict cleanly presented
   by its own facts.

2. **The ADA question was bypassed, not decided against advocacy.**
   The appellate opinion, pages 10–11 (App. 13(a)–14(a)), leaves the protected
   character of the asserted advocacy unresolved and holds that the record
   does not support causation. It relies on the lengthy interval before the
   challenged employment actions and the lack of other evidence of
   retaliatory motive. Recognizing third-party advocacy as protected would
   therefore not itself remove the stated basis for affirmance. I do not
   treat an assumed or reserved issue as a contrary circuit holding.

3. **The Rule 56 question is principally an evidentiary disagreement.**
   The panel states de novo review and the ordinary genuine-dispute standard
   on page 4, addresses alleged forged documents on page 8, and reaches
   the merits despite deficiencies in the pro se briefs. The petition
   vigorously disputes those conclusions, but does not identify a competing
   legal rule adopted by this panel. The appended reconsideration order,
   pages 3–6, also explains the distinction between new claims and evidence
   supporting pleaded claims, and addresses discovery and Rule 56 requests.
   Resolving the dispute in petitioner's favor would require substantial
   record examination rather than simply choosing between legal standards.

4. **The vehicle supplies little counterweight.** The decision is
   unpublished, unanimous, and on the non-argument calendar. The provisioned
   rehearing order records no request for an en banc poll. Those facts do
   not prove correctness, but supply no visible internal disagreement that
   would overcome the independent-ground and record-specific problems.
   Self-representation is not itself a reason to deny review; the concrete
   problem is how the issues were decided and presented.

These considerations reduce my estimate from the 5.104% class prior to
0.6%. That adjustment is judgmental, not a fitted estimate for pro se
employment petitions. I leave meaningful nonzero mass for an overlooked
legal development or a stronger reading of the full record. I have not
independently reviewed every discovery exhibit or the respondent's position.

## Other elicited forecasts and limitations

The 0.98 distribution increment is high because the starting count is zero;
the modal trajectory is one initial distribution and denial, not repeated
relisting. The 0.001 CVSG forecast reflects the case's subject and vehicle,
not a mistaken inference that a missing CVSG can never arise. The 0.35
summary-route figure is conditional on the rare grant, not an unconditional
35% chance of summary relief. No identified intervening decision affirmatively
supports a GVR. The 0.008 conditional denial-writing estimate and uniformly
small unconditional writer probabilities reflect the lack of a clean
controversy warranting a public statement. These numbers are subjective
forecasts; the committed pack supplies no matched estimate for them.

The stakes score of 0.22 recognizes potentially consequential Title VII and
ADA questions while distinguishing that possible reach from this petition's
individualized dispute and grant prospects.

The provisioned petition and appendix contain residual personal contact
information despite scrub metadata reporting zero residuals. I have neither
reproduced it nor used it; `flags.json` records the provisioning concern.
General-rule web retrieval attempts returned no usable content, so they
contributed no evidence. The only substantive external retrieval was the
preexisting *Lewis* decision, not this petition's current docket.
