# Rationale for the prediction

## Information set

This is a forward, cert-stage, response-requested cell. I read the case-level snapshot **2026-09-05.json**, cut to entries strictly before September 5, 2026; event.yaml; context.json; documents.json; questions-presented.txt; the petition's substantive argument; and the appendix's relevant lower-court opinion and rehearing order. The frozen context supplies sal-v4 band **baseline**, Term 2026, distribution_count **1**, and no CVSG. I use that band rather than deriving a stronger one from the petition. The United States is the respondent, not the petitioner, so the federal-petitioner floor does not apply.

The petition and appendix were filed August 20 and fetched October 26. Their later fetch dates do not turn these pre-cutoff filings into later substantive evidence. Both are marked nonempty, untruncated, and not OCR-derived. The record contains no brief in opposition or reply. That is the expected information set at the response-requested moment, not a provisioning defect; I do not infer the government's eventual recommendation. No amicus-brief filing appears in the four provisioned proceedings entries. The separate listing of NACDL counsel does not establish a filed brief or override context.amicus_briefs being null.

I did not retrieve this petition's current docket, outcome, subsequent history, or another cell's prediction. I do not know its disposition. All case-specific reasoning rests on the provisioned pre-decision record, despite the run occurring after its cutoff.

## Calibration

The matching sal-v4 table in metrics/statpack.md renders Terms 2017–2026. For this Term-2026 private petitioner I pooled **all nine strictly preceding rendered Terms**, 2017–2025, using the baseline band's bracketed **reached** risk sets, not the terminal-band figures. Exact fields in metrics/statpack.json give **660 grant-family outcomes / 12,913 weighted resolved petitions = 5.111%**. I exclude the 2026 row. This is the starting rate, not an estimate conditional on a response request or a developed split.

The paid-segment terminal relist buckets provide context rather than a forward hazard: zero relists has a grant-family rate of about 1.8% (resolved n=10,203), one about 13.7% (n=2,538), two about 41.2% (n=495), and three or more about 37.4% (n=484). The present single distribution is zero observed relists, but does not imply the petition will end there. The CVSG cut gives about 34.8% grant-family outcomes with a CVSG (n=164), versus 6.4% without one (n=13,556); this petition has none, and being a United States respondent makes a separate CVSG especially unlikely. These cuts pool Terms and overlap with the band; I do not multiply their marginal rates together.

The amicus cut's zero-brief bucket is about 3.8% grant-family outcomes (resolved n=11,109), but is measured at disposition, not this moment. The frozen amicus count is unknown and the docket excerpt cannot establish the eventual count, so I make no numerical amicus adjustment. The broader modern-cert and originating-circuit cuts are population cross-checks, not substitutes for the paid private-petitioner risk set.

## Why move from 5.1% to 38%?

The positive evidence is unusually substantial for a baseline-band petition:

- The Court affirmatively requested a response after the United States waived one. This is actual attention, although it does not establish four votes to grant. No committed response-request-conditioned base rate is available, so the adjustment is judgmental.
- The petition, pp. 11–17, identifies disagreement across several circuits, including recent published decisions, and a particularly close unpublished Ninth Circuit battery decision. It is not merely asking the Court to correct one sentencing calculation.
- The issue is preserved and dispositive. The petition, pp. 8–10 and 19–20, and appendix, pp. 4a and 18a–25a, show that excluding the Florida battery conviction would remove one of the three necessary ACCA predicates. The other two predicates do not independently sustain the enhancement.
- The petition presents one focused federal statutory question with consequences for a lengthy mandatory minimum. Its experienced Supreme Court counsel helps make the conflict and vehicle clear, but is not an independent reason to assume a grant.

The principal restraint is that the split's precision is contested. The Sixth Circuit's own opinion, appendix pp. 20a–25a, does not merely announce that any voluntary act suffices: it requires intentional force directed at a person and distinguishes Gomez on whether the California offense requires intent to apply force at all. It acknowledges and rejects Vega, but Vega is unpublished. The petition invokes later published authorities and analogous statutory structures; without the opposition and those separate opinions independently verified, I cannot regard the claimed two-versus-three division as fully established on identical elements.

There is also a serious substantive answer to petitioner: intent to touch another person could satisfy Borden's direction-of-force requirement, while actual great bodily injury supplies the necessary degree of force. Conversely, petitioner argues that Johnson and Borden together require the higher mental state to reach the injury-producing force, not merely a slight touch. This merits uncertainty supports plenary review if granted, not an assumption of obvious summary error. The Sixth Circuit's discussion of Thomas's different understanding of harm further complicates a simple application of Borden's vote count.

Balancing those considerations, **38%** is a substantial upward adjustment for a focused, consequential conflict plus a called-for response, but still leaves denial as the most likely result. It is not a measured response-request rate. The largest uncertainty is how the government will characterize the alleged conflict and vehicle.

## Other numbers and limitations

The 98% distribution increment reflects routine redistribution after the requested response, not a prediction of a substantive relist; this claim is masked at this moment. The 0.5% CVSG increment reflects the existing United States-party posture. The 12% summary-route figure is conditional on a grant and allows for an unexpected concession or intervening development without inventing one. The 10% denial-writing figure is conditional on denial. Per-Justice order-writing figures are unconditional, small, and allow correlated writings; they need not sum to one. Thomas receives the highest individual figure because his concurrence is expressly debated below, not because I predict any particular cert vote.

The stakes score **0.56** reflects national sentencing implications and potential relevance to parallel crime-of-violence provisions, balanced against a technical issue rather than a wholesale challenge to the statute. It is separate from the 38% grant estimate.

A structured corpus query returned five prior-Term grant examples, but none supplied a usable substantive ACCA analogy. It was disposition-selected and cannot estimate grant odds. Its bare 2026 clock filters docket Terms, not necessarily decision days; the returned October 2026 grants are permitted forward context but did not inform the case-specific probability. CourtListener's Delligatti lookup was throttled (HTTP 429), and two general-precedent web-search attempts returned no usable results. I therefore treat descriptions of precedent outside the provisioned lower opinion as the parties' or lower court's accounts, not as independently verified holdings. Retrieval attempts and the exact corpus transfer line appear in retrieval.md.
