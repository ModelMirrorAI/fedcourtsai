# Basis for the probabilities

## Information set

This is a forward, cert-stage forecast for Wealthy, Inc., et al. v. Spencer Cornelia, et al., Supreme Court No. 25-1329. The petition-kind event supplies no explicit stage; the contract's cert default governs. I read the September 17, 2026 snapshot, event definition, context, document manifest, questions presented, and relevant petition sections, especially printed pages 1–11 and 27–29. The petition was fetched July 18, is marked nonempty and untruncated, and has 53 pages. I did not read its separately linked appendix or the amicus brief.

The provisioned documents contain no opposition or reply despite the snapshot recording both. I retrieved selected pages of the **August 26 opposition** and **September 11 reply** directly from the specific Supreme Court PDF links already in the snapshot. These are pre-disposition advocacy, not subsequent docket history. They materially improved the assessment of vehicle quality. The scope and pages are logged in retrieval.md. I neither sought nor encountered this petition's disposition, and do not independently know it.

The snapshot's source creation date is September 16 and the provisioned snapshot date is September 17. Those dates describe this input, not a newly checked live docket. The frozen context is sal-v4, baseline, Term 2025, distribution_count 1, no CVSG. Both distribution notices refer to September 28; I retain the harness's count rather than treating duplicate scheduling notices as a relist. A requested opposition is not a CVSG.

## Base-rate anchor

I use the committed metrics/statpack.md sal-v4 **baseline bracketed reached** rates for all displayed Terms strictly before 2025: 2017–2024. This is the private-petitioner floor, not the government or whole-docket population. Weighting the displayed percentages by their displayed denominators gives approximately **5.12%**, with a summed weighted denominator of **11,580**. The calculation uses rounded published percentages, so it is not an exact numerator reconstruction. Neither the 2025 nor 2026 row enters the anchor. The leading terminal-band rates would wrongly assume this petition never advances.

The paid-segment relist and CVSG cuts supply shape, not a forward transition estimator. Their terminal buckets show sharply stronger grant rates after repeated distributions and a CVSG; they do not imply a 36% forward relist probability for this case. I do not use the pack's mixed-court timing statistic to forecast the conference outcome. The broader modern-cert and Ninth Circuit rates are less well-matched than the class-specific anchor.

These are committed-pack estimates, not a live corpus claim. The inspected statpack has no build/freshness timestamp; I did not query a remote corpus or ascertain its newest pull or snapshot stamp. That limits freshness claims, not the choice of the prescribed prior-Term anchor.

## Moving from approximately 5% to 14%

**Reasons to increase:** Question 1 identifies an entrenched disagreement over federal treatment of state anti-SLAPP motions rather than only alleging an erroneous result. The petition describes a distinct fee consequence even though the ordinary summary judgment remains in place. That creates a potentially meaningful legal issue beyond recovering the underlying defamation claim. The July response request demonstrates attention, and the filed amicus supplies a modest additional signal. The petition's reliance on Berk offers a recent doctrinal reason to revisit the issue, though I do not treat counsel's claimed extension as an established holding.

**Reasons not to go much higher:** The opposition, printed pages 5–11 and 20–25, raises preservation, independent Rule 56 grounds, unresolved proceedings, and the nonprecedential decision. Its public-figure discussion at pages 25 and 28 portrays Question 2 as fact-bound and potentially non-dispositive. I treat these as advocacy-supported risks, not adjudicated forfeiture or a proven absence of a split.

The reply, pages 4–8, counters that petitioners had won the special motion below, that fee entitlement is independently reviewable, and that Gopher Media concerned immediate appealability rather than this applicability question. Those answers preserve a meaningful grant chance but do not eliminate the vehicle dispute. I therefore do not treat the opposition's reference to Gopher Media's June 15 denial as dispositive negative precedent. That other petition's history, disclosed in these pre-decision briefs, is not this event's outcome.

My 14% is a judgmental adjustment, not a fitted regression or the product of estimated likelihood ratios. A clearer preservation record could move it upward; confirmation that the central question was neither pressed nor passed upon would move it downward. I discount Question 2 heavily because its framing challenges application of an accepted standard rather than presenting a comparably developed conflict.

## Other numbers

The **36% further-distribution** estimate reflects the response request and substantive issue against a first-conference posture and substantial denial risk. It is not inferred from two appearances of the same conference date. **1.5% CVSG** reflects the lack of a demonstrated governmental stake beyond ordinary federal procedure.

The **18% summary route conditional on grant** leaves room for a Berk-based GVR, but the contested distinction between procedure and surviving fee remedies favors plenary treatment if the Court takes the case. Berk predates the lower court's February decision according to the opposition, further weakening a straightforward intervening-decision story. The **6% separate writing conditional on denial** allows some concern over speech litigation without predicting a particular Justice's public action.

The **0.57 significance score** measures the potential reach of a federal anti-SLAPP ruling, not grant likelihood. Broad procedural and speech-litigation consequences justify an above-midpoint score; the particular private dispute and narrower second question keep it below a landmark constitutional case.

## Tool limitations

The browser returned no readable content for the exact filing URLs. A shell PDF extraction attempt failed because pdftotext is absent; in-memory HTTP retrieval and the installed pypdf reader succeeded. The default uv cache location was read-only; a temporary cache override made the prescribed CLI commands usable. No inputs or pipeline code were changed.
