# Evaluation: codex-baseline, Scroggins v. City of Shreveport (No. 26-383), cert petition

**Outcome:** petition denied on 2026-11-16 after a single distribution (conference of 2026-11-13); no call for a response, no CVSG, no noted dissent.

**Prediction:** `denied`, P(grant) = 0.007. Correct on the label; Brier = 0.000049. This is a cert-stage cell: the segment base rate and skill score are the harness's to stamp, and the claims block is scored in code. No votes are scored at this stage and no semantic set is declared.

## Reasoning quality: 0.88

The strongest rationale of the three. It read the petition and the appendix and grounds each adjustment in a cited page: no demonstrated split and the petition's own concession about error correction; an unpublished affirmance that announces no categorical rule; the district court's reliance on fitness-for-duty evidence rather than absences alone; the independent no-pretext holding that would survive a favorable ruling on qualification; and the abandoned due-process claim. I spot-checked the pretext and abandonment points against the staged appendix and they hold. Its base-rate handling is careful: it uses the frozen risk-set anchor, treats the terminal relist/CVSG/amicus cuts as shape rather than multipliers, and declines to use the current Term's row. It states the best argument for review and explains why a small grant tail remains, and it is explicit about what it did not retrieve and which tool calls returned nothing. Minor reservations: the final 0.7% is a judgmental landing rather than a derived figure, and it is the highest of the three probabilities for a petition with no response called, though still well calibrated.

## Predicted reasoning: 0.75

Central claims: denial without opinion after the Nov 13 conference, no further distribution, no CVSG, no separate writing. All are borne out. The document commits to the order list following the conference and adds accurate texture (a denial that announces no ADA rule), but that is entailed by any denial and earns nothing. As with the other candidates, the borne-out claims are the expected course for a waived pro se petition, which caps the grade below the top. The conditional QP and summary-route forecast is untested.

## Leakage

Forward cell: prediction written 2026-10-31, petition denied 2026-11-16. Read the snapshot dated 2026-10-31 (one distribution, no disposition). One call carries retrieved_doc_date 2026-10-26, before the resolution. Two web-search rows are unobserved; graded on their queries, they target Rule 10 and the Court's rules PDF, not this case. CourtListener calls were for Tolan v. Cotton (2014), a cited authority. The candidate states it did not retrieve this petition's docket or disposition, and the log is consistent with that. No retrieved_doc_date on or after the resolution date, no read of data/qp-topics/, and the reasoning does not presuppose the result. Graded `not_applicable`; not suspected.

## Big case

My own read is 0.03: Pro se, paid petition from a one-line unpublished Fifth Circuit affirmance of summary judgment in a single firefighter's ADA/retaliation suit against a city. No split alleged, respondent waived, no amici, denied at first conference without a call for a response or any writing. Stakes confined to the parties.
