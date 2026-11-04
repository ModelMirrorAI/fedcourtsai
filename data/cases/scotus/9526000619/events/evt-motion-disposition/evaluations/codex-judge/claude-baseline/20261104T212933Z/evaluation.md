# Evaluation: claude-baseline

## Outcome and mechanical scores

This is an **interim / arrival** cell. The outcome records denial on November 3, 2026, with `interim_reading: denied` and `interim_granted: 0`. The November 4 snapshot attributes denial to the Chief Justice. The label `denied` is correct: **correct = 1**. With P(relief) = 0.02, **Brier = (0.02 - 0)^2 = 0.0004**. The legacy binary and finer reading agree here.

Baseline and skill are for the harness to stamp. The committed statpack's application-Term pool for 2016–2025 has zero finer-resolved and 1,366 finer-unread applications, failing the 50-resolved floor and unread-zero coverage requirement. I supply no substitute rate. Interim votes are never scored, no semantic set applies, and mechanical claim scores are left to the harness.

## Rationale quality

**Reasoning quality: 0.75.** The rationale correctly identifies the arrival boundary, distinguishes interim from cert baselines, declines to use an ineligible finer-reading pool, and treats the missing application content as unknown rather than as adverse evidence. It expressly labels its speculation about the underlying private dispute as a guess rather than a fact driving its numbers. Leaving a nonzero tail for unseen substantive arguments is sensible.

The analysis is comparatively thin on the legal stay standard and on why this applicant cannot meet it. Broad assertions that government/represented matters account for almost all grants and that self-represented applicants often renew are not demonstrated by the cited marginal counts or a small recent sample. Referral and grant probabilities consequently remain judgmental rather than calibrated. The suggestion that an unusual constitutional question would change the probability only slightly understates the importance of the very filing the rationale could not read. A correct denial does not cure those evidentiary limits. This grade assesses only `reasoning.md`.

All candidates describe empty application text at prediction time. The evaluator now has readable OCR with `empty_text: false` and `ocr_derived: true`. That later filing confirms a possession dispute and an asserted federal due-process challenge to the adequacy of state appellate procedure. I do not fault claude-baseline for lacking the later OCR, and the provisioning difference is flagged.

## Predicted reasoning

**Forecast quality: 0.88.** The forecast specifically calls Chief Justice denial without a response request or initial referral, no amici, and a November disposition within about two weeks of docketing. Those central procedural claims are borne out by the November 3 denial and recorded outcome signals. Its timing is somewhat broader than a narrow date-window forecast, and it predicts little about the ground. The one-line/no-separate-writing claim remains unresolved without the order body or a writing record. Neither a possible renewal nor the hypothetical form of an unexpected grant is resolved by the initial denial; those conditional passages earn neither credit nor penalty. This is not a null-grade case because the disposition and procedural route are directly observable.

## Leakage assessment

The log identifies forward mode and marks all 13 results captured. One call fetches this application's live official docket. The reasoning and retrieval note say it contained only the submission/docketing information and no later entry. The staged log provides a digest, not the rendered returned page, so this is not independent page-content verification. Still, no query or prose affirmatively reveals the target denial; the other retrieved dispositions concern different applications. Forward retrieval of a live unresolved docket is not inherently leakage, even when it reaches beyond the frozen arrival snapshot. Prediction and resolution share November 3, but the record supplies no resolution time and does not establish the case was already decided when retrieved. Assessment: no affirmative outcome exposure, influence `not_applicable`, leakage suspicion false.

## Stakes

My independent significance assessment is 0.08. The staged application shows serious personal possession/housing stakes, with an individualized procedural due-process challenge and no demonstrated broad institutional consequences.
