# Rationale

## Call and information set

I assign a **70% probability of any grant** and predict a plenary grant of certiorari, not a decision on the merits now. The significance score, 0.74, concerns the stakes if decided, not the likelihood of review.

The baseline is `record/snapshots/2026-11-09.json`, read with `record/context.json` and the relist event definition. This is a forward, cert-stage cell, with a date cut at November 10, 2026, docket-number Term 2025, salience version sal-v8, and frozen band high. I used no later entry or outside account of this petition's disposition and have no known outcome to disclose.

The snapshot records three distributions: April 28 for the May 14 conference; October 7 for the November 6 conference after the invited government brief; and November 9 for November 13. The Court called for the Solicitor General's views on May 18, and the United States filed on September 15. Three distributions should not be mistaken for two successive, ordinary merits-screening relists: the middle distribution restarted consideration after the CVSG. The November 9 entry is nevertheless a genuine additional conference after consideration of the government's recommendation.

## Base-rate discipline

The placement-frozen `cert_anchor.rate` is **0.3455056179775281**. This is the appropriate prior-Term reached-high anchor, not the overall discretionary-cert rate. The matching sal-v8 table in `metrics/statpack.md` shows eight strictly preceding Term rows, 2017–2024, totaling n=712; their underlying rate corresponds to 246 grants. I exclude the petition's own Term 2025 and Term 2026 from this anchor. I do not reclassify a private corporation as a federal petitioner because the government supports it.

As cross-checks, the committed statpack's relist buckets 1, 2, and 3+ contain respectively 2,532, 495, and 483 resolved petitions. Pooling their granted and GVR counts in `metrics/statpack.json` gives 726/3,510, or **20.68%**. The CVSG bucket gives 48 grants plus 9 GVRs over 164 resolved petitions, or **34.76%**. These are terminal-state, all-Term, denial-reweighted cuts, not estimates of this petition's forward hazard and not independent signals to multiply. The relist cut also includes reschedules. Neither table conditions on an affirmative SG recommendation followed by an actual post-brief relist.

The structured corpus lookup returned selected examples of grants after CVSGs, including RiseandShine, Monsanto, Hikma, and Cisco, generally with three distributions. They illustrate a possible procedural sequence, not a representative sample: the lookup explicitly selected grants. I draw no empirical success rate from those five results.

## Why move above the anchor?

The strongest additional evidence is the actual recommendation, not the bare CVSG marker. `sg-invited-brief.txt`, printed pages 19–24, expressly recommends **granting** the petition. It asserts an inter-circuit conflict, exceptional operational importance to federal immigration detention, and a clean final-judgment vehicle. The government describes both intergovernmental immunity and statutory preemption, rather than seeking a hold or a GVR. A subsequent real relist is consistent with preparing a grant, although it can also precede a denial or separate writing. I do not count the CVSG again as an independent upward adjustment; it already helps define the high-band population.

The petition and its questions presented ask whether the Supremacy Clause permits Washington to treat immigration detainees in a contractor-operated federal work program as employees subject to the state minimum wage. The contractor-versus-government distinction, federal detention operations, and claimed disparity with state detainees provide an institutional reason to review beyond correcting a single damages award. The petition's introduction and `cert-reply.txt`, printed pages 1–7, maintain that the Ninth Circuit's approach conflicts with other circuits and prior immunity cases.

`decision-below.txt` matches the caption, consolidated appeal numbers, and judgment identified in the petition. It shows a published affirmance, a Bennett dissent, and decisions on intergovernmental immunity, preemption, and derivative immunity. `lower-court-docket.txt` records denial of en banc rehearing with dissents; the SG brief describes those disagreements. I rely on these provisioned materials, not a newly retrieved lower-court docket. Final judgments after trial and a definitive state-law construction reduce ordinary interlocutory and unresolved-state-law vehicle problems.

## Why not an overwhelming probability?

The opposition is substantive. Washington's BIO, printed pages 16–22, says the Third Circuit's CoreCivic decision distinguishes ordinary wage burdens from prohibitions on federal contracting and expressly distinguishes this litigation. A disputed extension of common doctrine is less certworthy than opposite answers to the same question. The State also says state and federal private contractors receive the same wage treatment, and that the federal reimbursement limit does not forbid GEO from paying more. I treat the asserted split as contested, not established.

The September 29 supplemental briefs strengthen that caution. Washington invokes Hencely and Menocal against expansive contractor protections and disputes the government's factual comparator. The detainees identify revised national ICE detention standards and argue that future wage disputes will arise under those new standards, reducing this old-contract case's prospective importance. They expressly do not claim formal mootness. These are respondents' characterizations of the new standards and recent decisions; I have not independently resolved their applicability. The petitioner's reply likewise addresses recent contractor decisions rather than identifying an uncontested new decision requiring vacatur.

As limited doctrinal background, a CourtListener lookup of **United States v. Washington, 596 U.S. 832 (2022)** confirmed the rule protecting the federal government and its contractors against discriminatory state laws. That case does not itself establish that this generally worded wage law discriminates. The two sides disagree about the relevant comparators and practical operation. That difference counsels against a confident summary reversal.

Balancing the affirmative SG recommendation, real relist, and federal operational stakes against the contested split and changed-standards objection produces 0.70. The adjustment is judgment, not a published SG-recommendation-conditioned estimator. Denial remains a serious alternative.

## Ancillary probabilities and limitations

I give another distribution a 0.42 probability, allowing for further review or preparation of a writing while making decision at the already scheduled conference the more likely path. The zero CVSG increment reflects an invitation already on the docket; the claim is vacuous here, not a forecast that there was no invitation. Conditional on a grant, I give disposition in the cert order a 0.10 probability: there is no clear uncontested intervening ground for a GVR and the issues favor full briefing. Conditional on denial, I assign 0.28 to a dissent or statement. Order-writer probabilities are unconditional, with the highest small probabilities on Thomas, Alito, and Gorsuch; most probability remains on no writing at all. No cert-stage merits vote or majority author is forecast.

The provisioned combined BIO is explicitly truncated, ending during the detainees' argument. The State's argument and both subsequent supplemental briefs mitigate, but do not eliminate, that gap; `flags.json` records it. There is no separately provisioned appendix. The full petition includes appendix material, and I do not infer that any missing separate file means the underlying record was absent. Web searches and an official-opinion open returned no usable content; CourtListener supplied the limited historical precedent check. An initial CLI cache error was resolved by using a writable temporary cache with `--no-sync`, without installing anything.
