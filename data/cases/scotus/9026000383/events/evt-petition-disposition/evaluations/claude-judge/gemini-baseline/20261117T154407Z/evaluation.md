# Evaluation: gemini-baseline, Scroggins v. City of Shreveport (No. 26-383), cert petition

**Outcome:** petition denied on 2026-11-16 after a single distribution (conference of 2026-11-13); no call for a response, no CVSG, no noted dissent.

**Prediction:** `denied`, P(grant) = 0.002. Correct on the label; Brier = 0.000004. This is a cert-stage cell: the segment base rate and skill score are the harness's to stamp, and the claims block is scored in code. No votes are scored at this stage and no semantic set is declared.

## Reasoning quality: 0.85

A thorough, record-grounded rationale. It cites the appendix closely, and the figures I spot-checked against the staged appendix are accurate: 1,153 of 1,779 workdays missed (64.6%), the four-hour light-duty schedule, the Rule 47.6 affirmance, the alternative no-pretext holding, the reduction to a 45-day suspension and the abandoned due-process claim. It identifies the alternative holding as what insulates the judgment from QP 1, which is the decisive vehicle point. It also found and used the petitioner's earlier petition (No. 26-80), denied after a single distribution weeks earlier, a relevant and legitimately available prior that the other candidates did not use. Base-rate use is correct in substance: frozen risk-set anchor, with the terminal baseline and relist-0 rates as a lower reference. Reservations: it stacks several overlapping terminal cuts (amicus, CVSG, circuit) without noting that they overlap; the opinion is called 'two-sentence' where the record shows a short unpublished per curiam; and 0.2% with 0.99 confidence is aggressive, leaving very little room for a Tolan-style summary action, although the reasoning for going that low is laid out.

## Predicted reasoning: 0.78

Central claims: denial out of the Nov 13 conference on the Nov 16 order list without a request for a response, no relist or reschedule, no CVSG, no separate writing. All are borne out, and this is the most specific of the three documents: it names the order-list date, which is the date the docket records. That date follows mechanically from the conference date, so it adds only a little, and the overall forecast remains the expected path for a waived pro se petition. The conditional QP forecast is untested. One internal wrinkle, not docked: the document gives a 65/35 plenary/summary split and then says neither route is viable.

## Leakage

Forward cell: prediction written 2026-10-31, petition denied 2026-11-16. Read the snapshot dated 2026-10-31 (one distribution, no disposition). Every call is outcome_only, so results were not captured and the calls are graded on their queries: local record files, statpack, a corpus query for the petitioner's earlier petition No. 26-80, and CourtListener opinion searches by case name for the earlier Fifth Circuit appeal and for Weber v. BNSF. No. 26-80 is a different petition denied Oct 5, 2026, before the prediction; its disposition is legitimate forward signal, not this event's outcome, and the candidate disclosed it. The opinion search by this caption could not return a cert disposition that did not yet exist. No retrieved_doc_date on or after the resolution date, no read of data/qp-topics/, and the reasoning does not presuppose the result. Graded `not_applicable`; not suspected.

## Big case

My own read is 0.03: Pro se, paid petition from a one-line unpublished Fifth Circuit affirmance of summary judgment in a single firefighter's ADA/retaliation suit against a city. No split alleged, respondent waived, no amici, denied at first conference without a call for a response or any writing. Stakes confined to the parties.
