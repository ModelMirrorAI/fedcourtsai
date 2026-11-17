# Evaluation: claude-baseline, Scroggins v. City of Shreveport (No. 26-383), cert petition

**Outcome:** petition denied on 2026-11-16 after a single distribution (conference of 2026-11-13); no call for a response, no CVSG, no noted dissent.

**Prediction:** `denied`, P(grant) = 0.004. Correct on the label; Brier = 0.000016. This is a cert-stage cell: the segment base rate and skill score are the harness's to stamp, and the claims block is scored in code. No votes are scored at this stage and no semantic set is declared.

## Reasoning quality: 0.72

The rationale reaches a sound number by a clear, explicit route: start from the frozen band anchor, then discount heavily for a pro se petitioner, a waived response with no call for one, fact-bound error-correction questions with no split alleged, and an unpublished unexplained affirmance. The decomposition P(call for response) x P(grant | response) is the right structure for a waived paid petition and gives a transparent 0.4%. The weakness is depth: the candidate says it did not read the appendix in depth, so it missed the strongest vehicle problems the record offers (the district court's alternative no-pretext holding and the abandoned due-process claim), and it relied on the petition's own description of the decision below. The pro se discount is asserted rather than sourced. The limits are candidly disclosed. Sound and well calibrated, but thinner than the record allowed.

## Predicted reasoning: 0.72

Central claims: denial at the first conference, no call for a response / relist / further distribution, no CVSG, no separate writing. All four are borne out by the docket and the outcome. They are stated flatly rather than hedged, and tying the denial to the Nov 13 conference with no intervening call for a response is a real commitment, though for a waived pro se petition it is also what nearly any competent reader would have called, so the document cannot reach the top of the scale. The QP-selection and summary-route content is conditional on a grant and earns neither credit nor penalty.

## Leakage

Forward cell: prediction written 2026-10-31, petition denied 2026-11-16. Read the snapshot dated 2026-10-31 (one distribution, no disposition). Log is fully captured: local record files, statpack, and two generic denied-case corpus queries; no own-case docket or web retrieval. No retrieved_doc_date on or after the resolution date, no read of data/qp-topics/, and the reasoning does not presuppose the result. Graded `not_applicable`; not suspected.

## Big case

My own read is 0.03: Pro se, paid petition from a one-line unpublished Fifth Circuit affirmance of summary judgment in a single firefighter's ADA/retaliation suit against a city. No split alleged, respondent waived, no amici, denied at first conference without a call for a response or any writing. Stakes confined to the parties.
