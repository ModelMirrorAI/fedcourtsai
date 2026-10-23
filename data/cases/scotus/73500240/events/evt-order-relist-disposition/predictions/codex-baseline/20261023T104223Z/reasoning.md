# Basis for the prediction

## Information set

This is a forward, cert-stage, first-relist cell. I used the case-level `record/snapshots/2026-10-07.json`, the event definition, `context.json`, `documents.json`, the questions presented, and relevant portions of the petition and opposition, including the panel opinion and en banc order reproduced in the petition's appendix. The snapshot is bounded strictly before October 8, 2026; I did not retrieve subsequent developments in this case. Although the run occurs on October 23, the forecast uses the provisioned October 7 information set rather than assuming that the run date supplies additional proceedings. I do not know this petition's disposition.

The frozen conditioning is sal-v4, elevated, docket-number Term 2025, two distributions, and no CVSG. The September 17 response-request entry was expressly removed as erroneous; I do not treat it as additional judicial attention. In contrast, the September 22 record request and September 28 receipt of the district-court record are affirmative, usable signals. They predate the first conference and are not evidence of a second relist. The November 6 conference is a scheduled future consideration, not a disposition.

Both substantive filings have extracted, untruncated, non-OCR text according to the manifest. No reply or full amicus text was provisioned. I did not inspect the actual recordings or autopsy: descriptions of them come from the competing filings and the appended judicial opinions. Those descriptions must not be treated as my independent factual findings.

## Base-rate anchor

I used the committed `metrics/statpack.md` and its JSON companion, not a live corpus query. The matching sal-v4 elevated band's bracketed reached rates, pooled across every displayed Term strictly before this case's Term 2025, yield **484 grant-family outcomes / 2,810 weighted resolved risk-set members = 17.224%**. The included Terms are 2017 through 2024. I excluded both 2025 and 2026, even though the cell is forward and the current calendar year is 2026. This is a reached-band prior, not the lower rate among petitions that terminate in elevated.

As the relist-moment cross-check, pooling terminal relist buckets 1, 2, and 3+ gives **712 grant-family outcomes / 3,489 weighted resolved petitions = 20.407%**. The constituent resolved counts are 2,521, 487, and 481, with 337, 198, and 177 grant-family outcomes. These cuts pool Terms and terminal histories: they are descriptive checks, not a strictly-prior, moment-matched estimator. The distribution parser also counts some preconference reschedules as relists, whereas this record actually proceeds past an earlier conference. The paid-segment CVSG cut shows grant-family shares of approximately 6.2% without a CVSG versus 34.8% with one, but those are terminal-status cuts, not hazards or independent multipliers. Nothing warrants treating the absence of a CVSG as an independent discount after using the salience anchor.

These numbers describe the committed statpack build, not freshly queried corpus state. I did not run `corpus-info`, pull a corpus blob, or establish a live corpus freshness stamp; I make no claim that these are current live-population counts.

## Why 36%, rather than the 17.2% anchor

The upward adjustment rests on case-specific evidence of potential summary correction, not on the relist alone:

- The Court requested and received the lower-court record before the initial conference. In a case whose decisive disagreement concerns recordings and competing factual inferences, that is consistent with genuine examination of a possible summary intervention. It is not proof of four votes or of the direction of review.
- The appended en banc order confirms a 9-8 denial of rehearing, with substantive dissents. The petition's application of qualified immunity therefore has a developed judicial advocate, rather than simply a disappointed litigant's assertion of error.
- The petition argues that the panel's clearly-established-law formulation is the same generality problem identified in Mullenix, and that an armed person fleeing a dangerous chase is materially unlike the panel's cited comparators. This makes a narrow summary-correction route more plausible than the broad Questions 2 and 3 would suggest on their own. These are the petition's legal arguments, not facts independently established by this forecast.

Substantial contrary considerations keep denial most likely:

- The panel's actual opinion identifies two factual disputes: the officer's perception of the handgun and whether Ramirez swung it toward the officers. It expressly sets out the plaintiff's burden to overcome immunity and the plaintiff-favorable summary-judgment rule. The petition's assertion that the panel inverted the burden is therefore not self-proving.
- The opposition emphasizes another officer's account, the post-shooting exchange, and wound trajectories to distinguish a dangerous armed-flight narrative from an immediate threat when the later shots were fired. The appended panel opinion provides support for the existence of those competing inferences, although it cannot resolve the video dispute for me. A fact-intensive disagreement is a substantial obstacle to certiorari, even when the subject is important.
- The opposition says the categorical Supreme-Court-only source-of-law question and the historical foundations question were not pressed or passed upon below. The appendix does not show a ruling on those broad theories. The asserted circuit conflict over the verbal elements of excessive force also looks less certworthy than a concrete outcome-determinative conflict. The split in the en banc vote is not itself a circuit split or proof that the constitutional law was unclear in 2021.
- The district court entered a final judgment for Granado, which the panel reversed and remanded. Thus the case now awaits further proceedings; I do not mistake it for a direct interlocutory appeal from a district-court denial of immunity. The remand posture nonetheless supplies a practical reason to await development below.

Balancing these considerations gives P(any grant) = **0.36**. This is a judgmental adjustment, not a fitted conditional estimate. The record request and qualified-immunity summary-correction theory justify a substantial increase, but not a majority-grant forecast.

## Other probabilities and stakes

The 55% additional-distribution probability reflects likely continued examination of the record or circulation of a summary disposition or separate writing. The terminal relist table does not publish that forward hazard; I do not derive 55% mechanically from its buckets. The 2% CVSG increment reflects the predominantly fact-bound state/local policing dispute and absence of an identified reason to solicit federal views.

The summary-route probability, 82%, is conditional on a grant, not 82% of all outcomes. Combined with the grant forecast it implies about 29.5% unconditional summary grant-side relief and 6.5% plenary review. A grant-side forecast would most naturally mean a summary reversal addressing qualified-immunity specificity. The opposition also reports an amicus request for a GVR in light of Zorn; I use that only as a provisioned description of an alternative route, not as an independently verified account of that decision's holding. The 20% conditional probability of a denial-related writing recognizes the close lower-court division and record attention without projecting named Justices' cert votes.

The significance score of 0.58 reflects the national importance of police lethal force and immunity, but discounts the probability that this particular vehicle would produce a broad rule. It measures stakes if decided, not the chance of a grant.

## Limitations

General-precedent web lookups returned no usable content, so no external decision text or search-result substance informed the forecast. The most consequential unresolved input is the recordings themselves. I have no independent basis to say that they blatantly contradict either side, and no basis to turn the record request into a directional vote count. No case-outcome material was encountered.
