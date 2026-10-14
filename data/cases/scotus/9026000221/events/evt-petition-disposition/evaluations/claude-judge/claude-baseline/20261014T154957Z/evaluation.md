# Evaluation: claude-baseline, Purdy v. Kansas (No. 26-221), evt-petition-disposition

**Cell.** Cert stage, forward mode. The petition was denied on 2026-10-13 at its first distribution (`actual_granted` 0, no noted dissent, no relist, no CVSG).

**Scores.** The candidate predicted `denied` with P(grant) = 0.03, so `correct` = 1 and Brier = 0.0009. The prediction froze the `baseline` band under `sal-v4`, so the stamped segment base rate and the skill score are the harness's. Vote accuracy is not scored on a cert cell, and there is no semantic block.

**Reasoning quality: 0.82.** This is a strong, specific rationale:
- It anchors on the reached baseline rate over prior Terms (about 5.0%) and notes how that rate varies across Terms.
- It reads the Kansas Court of Appeals opinion directly. From it, it identifies the 60-1507 / Strickland posture, the alternative prejudice holding (the same accusation came in through another agent over objection, plus repeated confessions), and the unpublished intermediate-court vehicle.
- It correctly treats a grant without a response as nearly unheard-of, so the grant path runs through a call for a response that had not happened.
- It weighs the split honestly and checks the cited circuit decisions on CourtListener.
- It adds a thin but relevant originating-court cut and says it is thin.

The deductions:
- It asserts that the Court denied cert on the same split last Term in "Reed v. Fredrick (cert denied 2025)", and its log records no check of that denial.
- It describes the case as "on direct review under section 1257 rather than habeas" alongside its own, correct description of the posture as collateral. The point it is making, a state judgment free of AEDPA deference, is sound, but the label muddies it.

Neither error changes the conclusion.

**Leakage.** Forward cell, graded `not_applicable`. Capture coverage is 1.0. Every legible `retrieved_doc_date` predates the 2026-10-05 prediction, and the docket search for 26-221 returned nothing. The corpus queries surfaced other petitions' denials, not this one. No outcome material for this petition was retrieved.

**Big case.** My own read is 0.25 (see `big_case.notes`).
