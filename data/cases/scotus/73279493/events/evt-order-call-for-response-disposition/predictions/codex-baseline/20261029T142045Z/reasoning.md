# Rationale

## Information set

I forecast denial with P(any grant) = **0.12**, using the cert-stage
response-requested moment. I read the case-level snapshot
`record/snapshots/2026-02-03.json`, `record/context.json`, the event definition,
`questions-presented.txt`, `documents.json`, the petition's substantive
arguments, and the pertinent portions of its reproduced Eleventh Circuit
opinion, especially Appendix A, pages 9a–16a. The lower-court decision is
pre-petition evidence, not the Supreme Court disposition being predicted.

The frozen context is forward, Term 2025, baseline under sal-v4, with one
distribution and no CVSG. The cutoff is February 3, 2026. The latest baseline
docket entry is the February 2 response request; the response is due March 4.
No opposition is provisioned, as expected at this moment, and I do not infer
its arguments. Neither a respondent waiver nor a completed conference is
shown, so neither is assumed. The earlier time-extension application is not
the substantive event being predicted.

The petition was filed December 2, 2025. Its manifest records a later fetch
and text truncation; the visible pipeline markers identify omitted appendix
material. I use the petition's argument and the reproduced appellate decision,
not the omitted material, and do not interpret an omission as silence. No
post-baseline history of this petition was sought. I do not know its eventual
Supreme Court disposition.

## Base-rate anchor

The committed statpack's sal-v4 heading matches the frozen context. I pool
the baseline band's bracketed reached rates for all eight rendered Terms
strictly before 2025, namely 2017–2024. Using the companion JSON's unrounded
prefix rates and weighted resolved counts gives **607 estimated grants out
of 11,599 denial-reweighted resolved petitions, or 5.233%**. This is the
private-petitioner risk-set anchor, not the much lower rate among petitions
that terminate in the weakest band. I exclude Terms 2025 and 2026.

The paid-segment marginal cuts provide context, not independent adjustments:
the no-CVSG bucket has n=13,556 resolved and a 6.4% grant family (4.1% grants
plus 2.3% GVRs); the CVSG bucket has n=164 and 34.8%. Terminal relist buckets
have n=10,203, 2,538, 495 and 484 resolved for 0, 1, 2 and 3+ relists. Those
are endpoints, not the hazard from this cell's one-distribution state. The
zero-amicus bucket has n=11,109 resolved and a 3.8% grant family, but context
marks the count unknown and the snapshot's absence of entries establishes
only that no amicus appears in this baseline. I do not substitute zero for
the frozen null or infer the terminal count. No published table conditions
on a called-for response, so the response-request adjustment is judgmental.

These are figures from the committed statpack, not a newly refreshed corpus
census. Corpus-wide vintage could not be established: `fedcourts corpus-info`
does not support the cell's service backend. The case evidence's own vintage
is the February 3 truncated snapshot; it supplies no case `last_pulled` stamp.
I make no claim about current corpus counts or current case status.

## Why 12%, rather than the 5.2% anchor or a high grant probability

The affirmative response request moves the forecast up: the Court requested
adversarial briefing after initial distribution rather than leaving the
petition on an unopposed path. The published appellate decision squarely
addresses a recurring federal statutory question. The petition identifies
different circuit formulations of willfulness and frames an intelligible
question about subjective justification. These are reasons for a meaningful,
but modest, upward adjustment.

The central discount is vehicle and conflict quality. The petition groups
the Fifth and Eleventh Circuits together as objective approaches. But the
reproduced Eleventh Circuit opinion expressly requires intent to injure and
finds that Watson intended the confinement itself. Its malice discussion
relies on persistent demands for arrest after searches found no wallet and
threats against the officers' employment. That is not simply an inference of
injury from a careless act. A subjective-intent-to-consequences rule could
therefore yield the same outcome, even if the circuits disagree in other
settings. I cannot equate the petition's asserted broad split with a verified,
outcome-determinative conflict on this precise question.

Similarly, a sincere belief that the women stole the wallet need not be a
finding that every ensuing demand for detention was legally justified. The
petition's comparison of discharged slander liability with nondischargeable
confinement liability is rhetorically effective, but the appellate court
explains the difference by distinct intended injuries. That reduces the
apparent force of a clean conflict with Geiger and makes summary correction
less attractive. These are forecasting judgments based on the staged opinion,
not an adjudication of which interpretation should prevail.

The missing opposition limits confidence in the claimed split. A CourtListener
attempt to verify In re Su was throttled with HTTP 429; the two general web
queries returned no usable sources. I therefore treat the petition's accounts
of other circuits as advocacy rather than independently verified holdings.
The corpus query returned three unrelated grant-side rows, not matched
bankruptcy comparators; an exact Geiger citation query returned none with an
explicit sparse-coverage warning. Neither supports a case-specific frequency.

## Other judgments

The 0.985 distribution increment reflects ordinary redistribution after a
response, not an almost-certain grant signal; the harness masks this claim at
the response-requested moment. The 0.04 CVSG probability reflects a federal
statutory issue but no identified federal party or distinctive federal
administrative interest. The 0.10 summary-route probability is conditional on
grant and reflects the absence of a specified intervening controlling case
or an obvious, uncontested error in the reproduced decision.

The 0.035 dissent/statement probability is conditional on denial. Small
per-Justice order-writing probabilities are unconditional and allow overlap
between writers. Their total is compatible with that rare denial-writing
event and the small grant-side writing possibility; they are not a
categorical distribution. No cert votes are forecast. The stakes score of
0.31 reflects the potentially nationwide effect on intentional-tort debts,
discounted for a specialized and fact-sensitive vehicle, independently of
the probability that review is granted.
