# Evaluation — gemini-baseline — scotus/9026000249 (Quaid v. Granet, No. 26-249), arrival disposition

**Stage:** cert (arrival moment, forward). **Outcome:** denied 2026-11-09 after a single distribution; no CVSG, no noted dissent.

**Scores.** Predicted `denied` at P(grant) = 0.001 → `correct` = 1, Brier = 0.000001. The segment base rate and skill score are the harness's to stamp ("the stamped segment base rate").

## Reasoning (reasoning_quality 0.6)
This is the only candidate that read the petition and the question presented, which were provisioned in its cell's `record/documents/`. It correctly identifies the actual question: whether California's litigation privilege (Civ. Code § 47(b)) can categorically bar amendment. That is a request to correct how a federal court of appeals applied state law, which is a classic reason for denial. Combined with pro se status and no split, the conclusion is right and grounded in the petition itself. But the rationale is a single short paragraph. It names the anchor (about 6.5%) without showing how it was derived, and it says almost nothing about how it got from 6.5% to 0.001. The analysis is correct but thin.

## Predicted reasoning (predicted_reasoning_quality 0.55)
I treated these as central: denial at the first conference with no relist, no CVSG, and no separate writing. All held. The docket shows one distribution (11/6/2026) and a denial on Nov 9. Its claim about the grant-conditional question is conditional on an event that did not happen, so it is neutral. The document is accurate but generic for a petition of this kind. The grade is just above the 0.5 anchor because it ties its reasons to the actual question presented.

## Leakage
Forward cell, predicted 2026-08-28. The log shows reads of the provisioned cell only (event, context, snapshot, petition/QP/documents), plus the schema and statpack. There were no web or CourtListener calls. Capture coverage is 0.0, so every row is unobserved and I graded the reads on their targets. None could reach a disposition that did not yet exist. `influenced_prediction` = not_applicable.

## Semantic grades
None. This is a cert cell.
