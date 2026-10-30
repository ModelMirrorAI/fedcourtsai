# Rationale

## Call and information set

**P(any grant) = 0.08; predicted disposition: denied.** This is a forward cert-distribution cell. I read the provisioned October 29, 2026 snapshot, context, event definition, questions presented, document manifest, and relevant portions of the petition, its appendix, and the October 14 brief in opposition (BIO). I have not sought this petition's disposition or later history, and have not read another cell's output or topic-label artifacts. I do not know this petition's outcome.

The record shows two distributions: July 22 for the September 28 conference and October 28 for the November 13 conference. Between them, the Court requested a response August 14 after waiver and extended the deadline to October 14, when the BIO was filed. A reply was submitted October 28 but its text was not provisioned. There is no CVSG and one Atlantic Legal Foundation amicus brief. The second distribution follows obtaining the requested response; it is not clean evidence of a substantive relist after actual consideration. Nevertheless I retain the harness's frozen **elevated, sal-v4** band and count of **two**.

## Base-rate calculation

The committed statpack's sal-v4 elevated **reached** rates, pooled over all displayed strictly prior Terms OT2017–OT2025, give **536 weighted grants / 3,139 weighted resolved petitions = 17.0755%**. I computed this using the exact `prefix_est_grant_rate` and `prefix_weighted_resolved` fields in metrics/statpack.json and checked the corresponding table in metrics/statpack.md. OT2026 is excluded; the lower terminal-band figures are not the live-cell anchor. The whole modern-cert section has 1,282 grants/GVRs among 44,777 resolved petitions, about 2.86%, but that is not this selected elevated population.

The paid-segment terminal relist cuts show grant-family rates of approximately 1.8% at zero (n=10,203), 13.7% at one (n=2,538), 41.2% at two (n=495), and 37.4% at three or more (n=484). The CVSG cut shows 34.8% with a CVSG (n=164), versus 6.4% without (n=13,556). The one-amicus bucket shows 15.1% (n=1,162). These pooled terminal cuts describe population shape, not the forward hazard from today's state. Their overlapping evidence cannot be stacked as independent multipliers. The circuit cuts do not directly match a Georgia state-court petition.

These figures describe the **committed pack**, not a fresh corpus census. This case's provisioned snapshot is dated October 29, 2026. The corpus-wide newest-pull/newest-snapshot vintage could not be obtained: corpus-info rejects this cell's service backend. No current-corpus completeness claim or count is inferred from the query results.

## Why below the 17.1% anchor

**A substantial issue, but a disputed split.** The petition (particularly pp. 14–26) argues that Mallory's express Pennsylvania notice does not validate Georgia's judicially inferred consent, especially for Samsung's 1985 registration predating Klein in 1992. That raises a consequential fair-warning issue for multistate businesses. The BIO (pp. 24–31) answers that Pennsylvania Fire itself involved judicial construction and that differing state-law consent rules do not establish conflicting federal due-process holdings. I treat those as competing arguments, not as an independently verified post-Mallory constitutional split.

**Preservation is the strongest obstacle.** The petition (pp. 13–14) reproduces an appellate argument that decisional law supplies inadequate constitutional notice, but acknowledges that the Court of Appeals did not address it. The BIO (pp. 14–19) argues that neither Georgia Supreme Court certiorari petition properly presented the federal question, and that the appellate presentation was conditional or insufficient. Its discussion of the state petitions makes the vehicle objection concrete. I do not resolve whether this bar is jurisdictional or prudential: either can make certiorari unattractive. The unprovisioned submitted reply might materially change that assessment.

**An independent ground may preserve the judgment.** The BIO (pp. 19–24) identifies trial-level concessions and unanswered requests for admission said to establish specific jurisdiction independently of registration; it says Samsung's attempt to withdraw them came too late. The petition describes a wrongly named Samsung company and an approximately $10.9 million default judgment, but sympathy over that result does not remove state procedural issues. Purchase and injury in Georgia also weaken a policy framing centered on out-of-state forum shopping. I attribute contested waiver and admission assertions to the BIO rather than assuming them conclusively established.

**Attention is not four votes.** The response request and national constitutional implications support a meaningful chance of review. However, the second distribution appears substantially procedural, and preservation plus the alleged independent jurisdictional basis make this weaker than the average petition genuinely relisted for substantive consideration. Those features justify reducing the risk-set anchor to 8%, rather than either adopting 17.1% mechanically or dropping to the 2.86% whole-docket rate.

A relevant corpus prior, Cooper Tire & Rubber Company v. Tyrance McCall, No. 21-926, records denial June 30, 2023, consistent with the BIO. That modestly reduces the case for automatic follow-on review after Mallory; it is not a decision on the merits and does not eliminate Samsung's distinct retroactivity argument. The three other broadly filtered denial priors are not topic-matched and are not a base-rate estimate.

## Other probabilities and significance

I assign **24%** to at least one further distribution beyond two: a considered relist after the requested response is possible, but zero remains modal. **2%** for a new CVSG reflects private state litigation with no identified federal program needing executive views. **15% conditional on any grant** for a cert-order summary disposition reflects no staged intervening holding supplying an obvious GVR rationale; if the Court takes the constitutional notice issue, plenary treatment is more natural. **8% conditional on denial** for a dissent or statement allows for lingering disagreement about consent jurisdiction, while expecting a silent denial because of the vehicle.

Order-writer probabilities are independently low for all nine Justices. Barrett and Kavanaugh are tentative possibilities for discussing the notice boundary; no Justice is individually likely to write. These are case-specific judgments, not estimates derived from an unavailable writing-rate table. Joining a writing is not authorship. I omit optional cert votes, which are ordinarily not publicly ascertainable.

**Big-case score: 0.65**, measuring significance if decided, not grant likelihood. A nationwide rule on consent to general jurisdiction could affect forum choice for many businesses, though this dispute's procedural problems and local injury limit its suitability as the vehicle.

## Input and retrieval limitations

The manifest reports nonempty, non-OCR text for the principal filings; the petition's appendix is truncated with explicit pipeline markers. I did not read every appendix page or infer silence from omitted passages. No actual reply, separate amicus text, or SG brief was staged. A submitted reply's absence is not evidence of no rebuttal; no SG recommendation is inferred.

Two general web searches for the established 2023 Mallory precedent returned no usable results. CourtListener's citation lookup for 600 U.S. 122 returned HTTP 429, so I used the provisioned briefing and corpus context rather than direct REST fallback. The legal characterization is therefore the parties' predecision presentation, not a newly retrieved controlling opinion. The service-backend vintage limitation and all retrieval attempts are recorded in retrieval.md and tooling.json. No target-case outcome material surfaced.
