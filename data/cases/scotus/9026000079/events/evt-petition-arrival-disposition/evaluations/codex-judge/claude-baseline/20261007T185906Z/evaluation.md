# Evaluation: claude-baseline

## Outcome and numerical score

This is a cert-stage arrival-disposition event. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The predicted label, `denied`, matches exactly: correctness is 1. The grant-family probability was 0.025, so the Brier score is `(0.025 - 0)^2 = 0.000625`. A correct denial forecast does not establish why the Court denied review.

## Reasoning quality: 0.78

The rationale uses an explicitly identified prior-Term risk-set anchor, separates downward adjustments from countervailing possibilities, and candidly describes its evidentiary limits. In particular, it distinguishes the retrieved lower-court docket's dismissal from its own inference that the ground was jurisdictional, and acknowledges that neither the petition nor the memorandum body was available. That restraint and the explanation of what missing information could change the probability support a substantial score.

The numerical adjustment to 2.5% remains judgmental rather than demonstrated. The counsel-profile proxy, the inference from an unpublished disposition to settled law, and the speculation about a reviewability question provide limited support without the actual question presented. An attempted amicus filing below likewise does not establish a certworthy conflict. These weaknesses limit the analysis independently of its correct headline outcome. The denial supplies no merits holding with which to confirm those hypotheses.

## Baseline unavailable under the version rule

The prediction froze Term 2026, band `baseline`, and `salience_version = sal-v3`. The committed `metrics/statpack.md` table is headed `Segment base rate by salience band (sal-v4)`. Its identically named band cannot supply a baseline for the older version. Accordingly, `segment_base_rate` and `brier_skill_score` are omitted and `base_rate_basis` is null. No terminal fallback is used. The historical rate quoted in the rationale is not independently reconstructed from this differently versioned table, nor treated as erroneous merely because the table changed. The shared flags file records the mismatch.

## Leakage and scoring scope

The harness log records forward mode, 24 calls, and result-capture coverage 1.0. The prediction and calls date to August 16, before the October 5 resolution. The dated lower-court results and general corpus query are earlier still. There is no shown retrieval of this petition's disposition or reasoning that presupposes it. Capture digests are not full source bodies, but the recorded queries, dates, and prose support `retrieved_outcome_material = false` and `influenced_prediction = not_applicable`. The August 14 waiver was permissible forward context even though later than docketing; the evaluator's uncropped October snapshot is not substituted for the predictor's input.

Only `reasoning.md` determines reasoning quality. The pointed-to forecast was read for context, not graded. Mechanical claims remain for the harness; cert votes and semantic propositions are not scored. No independent big-case assessment is supplied.
