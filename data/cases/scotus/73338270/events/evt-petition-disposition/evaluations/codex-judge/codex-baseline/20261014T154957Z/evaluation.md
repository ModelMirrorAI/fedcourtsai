# Evaluation: codex-baseline

## Outcome and numerical score

This is a cert-stage evaluation of prediction run `20260924T182556Z`. The committed outcome records denial on October 13, 2026, with `actual_granted = 0` and no noted dissent from denial. The predicted label `denied` matches exactly: **correct = 1**. With P(any grant) = 0.04, **Brier = (0.04 - 0)^2 = 0.0016**. A low realized error on this event does not establish calibration across cases.

The prediction freezes an `elevated` band under `sal-v4`, Term 2025. Segment base rate, its basis, and Brier skill remain the harness's responsibility. The stamped segment base rate is the scoring anchor; I do not reproduce or independently endorse a second numerical baseline in this evaluation. Cert votes are unscored, no semantic grades apply, and mechanical claims are left to the harness. The forecast document is read only for context.

## Reasoning quality: 0.94

This is a particularly careful explanation of why a petition with positive docket signals still has a low estimated chance of review. It distinguishes two distributions from evidence of two substantive conference deliberations, while preserving the response request and amicus interest as genuine positive signals. It gives concrete, supplied-record reasons for discounting the petition: the opposition's report of the Curtis denial, an unpublished decision applying that precedent, a mismatch between the question's framing and the ruling below, and antecedent state-action and immunity questions. The supplied opposition supports those characterizations as litigants' arguments.

The strongest feature is evidentiary discipline. The rationale expressly distinguishes a related denial from a merits endorsement, lack of a developed split in the presentations from a comprehensive audit of appellate law, and litigants' assertions about medical products and rights from established facts. It recognizes correlation among the negative factors instead of multiplying separate penalties, and labels the final numerical adjustment as judgmental. Its separation of terminal descriptive cohorts from forward transition probabilities is methodologically sound. It also distinguishes the statistics artifact's vintage from remote-corpus freshness and identifies missing reply and amicus texts as limitations of its own input set.

The remaining limitation is that the precise 4% adjustment has no fitted or matched-cohort support in the rationale. An independent review of the contested authorities and additional briefing might have changed the assessment, and the candidate appropriately acknowledges that its analysis is bounded by supplied filings. These limits prevent treating the analysis as conclusive. The unexplained denial is consistent with the forecast but does not establish which, if any, of the proposed reasons the Court accepted.

The reasoning score reflects those qualities of `reasoning.md`, not agreement with the forecast document or success of any separately scored claim.

## Leakage and evidentiary limits

The log designates a forward cell. The September 24 prediction and all 27 call records precede the October 13 disposition. I reviewed every logged query and the staged rationale, forecast, and retrieval note. Twenty-four calls have captured results; three web calls are unobserved, yielding capture coverage of 24/27. Those three query Rule 10 or a generic official rules-guidance page, not this petition's disposition. The candidate reports no usable results, but absent captured results do not independently establish that the searches failed or found nothing.

The instruction-file search explicitly excludes the labeling-artifact path; it is not a read of those artifacts. The statistics-history lookup is restricted to the statistics artifact, not target-case outcome history. Related-case denials discussed in the rationale are attributed to the supplied opposition and predate this petition's resolution. No visible evidence indicates that this petition's outcome was retrieved or presupposed. Therefore `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.

The evaluator's later case context is not evidence of what the predictor's snapshot contained. The stakes assessment derives from the supplied question and threshold obstacles rather than the candidate's own numerical stakes score. No external legal authorities or new case facts were retrieved for this evaluation.
