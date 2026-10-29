# Rationale for the prediction

## Information set

This is a **forward, cert-stage, distribution-moment** forecast for Supreme Court
docket 26-29, Mead Johnson & Company, LLC, et al. v. Greear, et al. I used the
case-level `record/snapshots/2026-10-29.json`, `record/context.json`, the event
definition, and the provisioned `questions-presented.txt`, `petition.txt`,
`appendix.txt`, and `documents.json`. Context freezes `sal-v4`, band `baseline`,
Term 2026, one distribution, and no CVSG. Its cutoff is null. The snapshot is
the October 29 provisioned record, not an independently refreshed live docket.

The petition and appendix are marked nonempty, untruncated, and not OCR-derived.
I read the questions presented, the petition's account of the facts and grounds
for review, and the appendix's actual appellate discussion of general and
specific jurisdiction, particularly paragraphs 16-23 and 36-43. The petition's
account is advocacy, not an agreed statement of facts. No brief in opposition
or reply was provisioned; the record instead shows the requested response due
October 30. That is an ordinary pending filing, not a provisioning defect, and
I do not infer that respondents concede any issue.

I did not retrieve this petition's outcome, later docket history, another cell's
prediction, or labeling artifacts. I have no known disposition of this petition
to disclose. External legal retrieval concerned only older, general precedent.

## Numerical anchor

The committed `metrics/statpack.md` supplies the relevant **sal-v4 baseline
band's bracketed reached rates**, not the rates among cases ending in baseline.
Pooling every displayed Term strictly before 2026, namely 2017-2025, with the
exact corresponding fields in `metrics/statpack.json`, gives **660 estimated
grant-family outcomes / 12,913 weighted resolved risk-set cases = 5.111%**.
The calculation sums `prefix_est_grant_rate * prefix_weighted_resolved` and
divides by the sum of `prefix_weighted_resolved`. These are denial-reweighted
estimates, not an unweighted sample of 12,913 individually retrieved petitions.
I exclude the 2026 row and do not confuse the roughly 1% terminal-baseline
rates with the rate this live private-petitioner risk set faces.

The modern discretionary-cert disposition table supplies a broader check:
692 plain grants plus 590 GVRs among 44,777 resolved estimated petitions,
approximately 2.86%. It is not the selected-segment anchor. The paid-segment
cross-sections provide shape rather than independent multipliers:

- Terminal relist 0: 10,203 resolved, approximately 1.8% grant family; relist 1:
  2,538 resolved, approximately 13.7%; relist 2: 495 resolved, approximately
  41.2%; relist 3+: 484 resolved, approximately 37.4%.
- No CVSG: 13,556 resolved, approximately 6.4% grant family; CVSG: 164 resolved,
  approximately 34.8%. These are terminal statuses, not forward hazards.
- Two or more amicus entries: 1,449 resolved, approximately 22.9% grant family.
  The snapshot shows three plainly docketed amicus briefs and one motion to
  file an amici brief, placing it above the two-entry threshold either way.
  These correlated, terminally measured cuts cannot justify multiplying odds.

All these figures describe the committed statpack available to this cell, not a
claim about a freshly polled corpus. A small service query returned three
resolved prior-Term denials; they were selected on denial, were not close
substantive analogues, and contribute no estimated success rate. Their tracking
stamps were masked. `corpus-info` cannot report corpus-wide vintage through this
cell's service backend, so I cannot independently state the newest pull or stored
snapshot date for that corpus. The numerical anchor comes from the committed
pack, not an asserted fresh remote count.

## Why move upward to 22%?

First, the specific-jurisdiction analysis presents a substantial apparent
precedent conflict. The appendix affirms jurisdiction on the basis of Illinois
marketing and product contacts notwithstanding these plaintiffs' out-of-state
exposure and injuries (Pet.App.19a-21a). *Bristol-Myers Squibb Co. v. Superior
Court*, 582 U.S. 255, 264-265 (2017), rejects a comparable substitution of a
defendant's general forum activities for a claim-specific connection. The
petition's discussion of *Ford Motor Co. v. Montana Eighth Judicial District
Court*, 592 U.S. 351, 362, 369-370 (2021), also supplies a serious argument that
relaxed causation does not remove the required forum-litigation link.

Second, the general-jurisdiction ground is not merely a discretionary venue
choice. The appellate court relies on historical headquarters and continuing
Illinois contacts (Pet.App.10a-13a), raising a genuine question about applying
the corporate at-home rule. *Daimler AG v. Bauman*, 571 U.S. 117, 137-139 &
n.19 (2014), distinguishes ordinary substantial business contacts from the
exceptional circumstances necessary outside incorporation and principal place
of business. I verified the exceptional-case discussion through CourtListener.

Third, the Court affirmatively requested a response after distribution, and
several business and medical organizations filed amici. That combination
supports an appreciable upward adjustment from the unconditioned baseline
risk set. It does not prove four votes to grant: no committed table conditions
on a requested response, so that adjustment is judgment rather than a measured
likelihood ratio. The 2+ amicus cut is a useful scale check for a forecast near
22%, not a fitted estimator for this petition.

## Why denial remains the main call

The petition largely requests correction of an allegedly serious application of
established doctrine, not resolution of a demonstrated, mature split among
appellate courts. Its questions are broad and the judgment has two independent
jurisdictional supports. The appendix records respondents' contrary factual
account: public representations still identifying Illinois as headquarters,
continuing nationally directed marketing employees there, and a disputed
completion date for the move. These details complicate treating the case as a
clean legal question with every relevant fact conceded (Pet.App.10a-13a).

The comparison to *Bristol-Myers* also needs care. The older case expressly
records that product development and marketing-strategy work occurred outside
the forum. Here, the extent to which actual claim-linked conduct occurred in
Illinois is less clear from the supplied materials. A residence or injury
outside Illinois is not, by itself, a universal jurisdictional immunity. I do
not adopt the petition's strongest assertion that the two records are identical.

The litigation is interlocutory. The petition acknowledges that posture and
argues that delay would impose large costs (petition pp.31-32), but its
jurisdiction section simply invokes section 1257(a). *Cox Broadcasting Corp.
v. Cohn*, 420 U.S. 469, 477-483 (1975), recognizes exceptions permitting review
despite remaining state proceedings. Thus interlocutory posture is a real
finality/vehicle uncertainty and a discretionary reason for caution, not a
demonstrated absolute jurisdictional bar in this case. I have not assumed that
an exception necessarily fails or that litigation cost alone establishes it.

These considerations keep the probability well below even odds despite the
substantial asserted constitutional error. **22%** is my subjective integrated
forecast, not an empirically fitted response-request/amicus model. The main
uncertainty is how convincing the forthcoming opposition will be on the actual
Illinois nexus, finality, and the breadth of the preserved issues.

## Other commitments and stakes

The **98% redistribution probability** is high because the already-requested
response makes renewed circulation the ordinary next scheduling step. It is
not a prediction of a 98% chance of a substantive post-conference relist. The
**4% CVSG** estimate reflects a constitutional dispute with indirect rather
than central federal regulatory interests. **40% summary route conditional on
grant** allows serious correction under existing precedent but discounts a
clean summary reversal because both jurisdictional grounds require attention.
**8% writing conditional on denial** reflects the possibility of a jurisdictional
statement while recognizing that the modal denial carries no explanation. The
per-Justice writing numbers also include the less likely summary-grant branch;
their sum is not a probability of at least one writer.

The **0.66 stakes score** concerns nationwide jurisdictional rules and the
location of substantial product litigation. The petition's claimed implications
for nutrition supply increase the potential importance, but I treat those
claims as advocacy and make no medical or product-safety finding. A grant
would not itself resolve causation, damages, or product liability.
