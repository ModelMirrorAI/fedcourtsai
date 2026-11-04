# Evaluation: codex-baseline

## Outcome and mechanical scores

This is an **interim / arrival** cell. The committed outcome records denial on November 3, 2026, with `interim_reading: denied` and `interim_granted: 0`. The November 4 snapshot expressly attributes denial to the Chief Justice. The predicted label `denied` is correct: **correct = 1**. With P(relief) = 0.03, **Brier = (0.03 - 0)^2 = 0.0009**. The legacy binary and finer reading agree here.

The baseline and skill are the harness's to stamp, not numbers supplied by this evaluation. The currently committed statpack has zero finer-resolved applications and 1,366 finer-unread applications across strictly prior application Terms 2016–2025. It cannot supply the finer-reading baseline: the resolved pool is below 50 and unread coverage remains. No replacement rate is used. Votes are not scored on interim cells; neither semantic grades nor harness-computed claim scores are written.

## Rationale quality

**Reasoning quality: 0.90.** The rationale carefully separates a stay application from certiorari disposition, identifies the appropriate demanding stay framework, and distinguishes an unreadable filing from a nonexistent or deficient filing. It refuses to invent the underlying dispute or substitute a cert rate, unrelated corpus denials, or the older interim reading for an eligible baseline. The small but nonzero probability is explicitly judgmental and acknowledges that the missing filing could change the assessment.

The analysis remains necessarily generic: it cannot assess the applicant's federal question, preservation, procedural-bar arguments, or particular equities, and its exact 3% calibration is not empirically established. Those limitations prevent a perfect grade; the successful label alone does not establish calibration. This score evaluates `reasoning.md`, not the forecast or the structured claims.

All candidates report that their prediction-time application text was empty. The evaluator's later provision now contains readable OCR, with `empty_text: false` and `ocr_derived: true`. The application asserts that disproportionate application of state appellate rules foreclosed review of a federal due-process claim and seeks both an administrative stay and a stay pending certiorari. That later evidence clarifies the case; codex-baseline is not penalized for lacking it. The provisioning difference is recorded in the cell flags.

## Predicted reasoning

**Forecast quality: 0.90.** The document specifically calls direct denial by the Chief Justice, no referral or response request, no amicus increase, and disposition during November 3–17. The staged outcome and docket bear those procedural and timing claims out. This is more discriminating than a generic denial forecast. The proposed absence of reasons, new doctrine, and separate writings is unresolved because no disposing order body or writing inventory is staged; the short docket entry is not a substitute. Conditional discussion of an explanation is neither confirmed nor treated as a failure. These findings affect only the forecast fields.

## Leakage assessment

The log identifies forward mode and contains 29 calls, with 26 captured results. The three unobserved web calls sought general stay authorities; their missing results are not evidence of failed or empty retrieval. Corpus retrieval and CourtListener verification concern other cases, not this application's resolution. Neither the log nor prose shows the November 3 denial being encountered. The prediction was also made November 3, but the record gives no resolution time, so the calendar-date coincidence alone does not establish prior knowledge or a misprovisioned decided case. Assessment: no affirmative outcome retrieval, influence `not_applicable`, leakage suspicion false.

## Stakes

My independent significance assessment is 0.08, based on the staged application's individualized possession dispute and procedural due-process question. Personal housing consequences are serious; broader precedential or institutional reach is not demonstrated.
