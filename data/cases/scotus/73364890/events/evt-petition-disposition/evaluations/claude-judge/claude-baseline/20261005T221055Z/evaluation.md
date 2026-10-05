# Evaluation of claude-baseline — F.E.B. Corp. v. United States, No. 25-1294

**Outcome.** Petition denied on the 2026-10-05 order list after a single distribution for the 2026-09-28 conference; no CVSG, no relist, no noted dissent. `actual_granted` = 0.

**Prediction.** `denied`, P(grant) = 0.005. Correct on the disposition axis.

## Scores

| field | value | how |
| --- | --- | --- |
| correct | 1 | `denied` == `denied` |
| brier_score | 0.000025 | (0.005 − 0)² |
| segment_base_rate | 0.0512 | baseline band, bracketed `reached` figure, sal-v4 table in `metrics/statpack.md`, pooled resolved-weighted over Terms 2017–2024 (592.9 / 11,580 = 0.051203, held as 0.0512) |
| base_rate_basis | risk_set | the prediction froze `band: baseline` under `salience_version: sal-v4`, and the table heading names sal-v4 |
| brier_skill_score | 0.990463 | 1 − 0.000025 / (0.0512)² |
| reasoning_quality | 0.88 | see below |

The case's Term is 2025; the table renders 10 of 10 Terms, and the strictly-prior rows with a baseline figure are 2017–2024, so the rendered window and the pack's window coincide and no window divergence needs flagging. This is a cert cell, so Brier, rate, basis and skill are mine; `correct` is also written per contract for the stamp's comparison. No `vote_accuracy` (cert stage), no `semantic_grades` (no declared set), no `claim_scores` (harness-computed).

## What the reasoning got right

- It anchored on the correct figure: the bracketed reached rate for the frozen baseline band under the matching salience version, pooled over strictly-prior Terms, and reproduced the pooling (593 / 11,580 ≈ 5.1%) exactly as the evaluator scores it.
- It identified the decisive signal: the Solicitor General's waiver on June 16 followed by distribution with no call for a response. Its statement that the Court does not in practice grant a paid petition without first calling for a response is the right reading of Rule 15 practice and is what makes a first-conference denial the near-certain path.
- Its reading of the questions presented is accurate: QP1 asks whether the Court "should address" a 1985 concurrence rather than stating a legal question, and QP2 restates Anderson's own holding on clear-error review of documentary findings. The petition pleads no circuit split and no conflict with this Court's precedent.
- The vehicle analysis (unpublished per curiam, fact-bound intent findings about 1920s and 1940s dredge spoil, a short argument section) is grounded in the provisioned petition and the appended Eleventh Circuit opinion, not asserted.
- It verified pendency by a CourtListener docket lookup (date_terminated null, last modified at the June 24 distribution) and disclosed that the September 15 poll could miss a later call for a response. That is the right uncertainty to name on a forward cell.
- The side claims are reasoned consistently with the headline: no CVSG because the United States is the respondent, a low relist figure for a waived no-split petition, and dissent-from-denial near zero with no Justice on record about Anderson.

## Where it is weaker

- 0.5% is the lowest of the three numbers. It is defensible given the signals, but the residual it names (a surprise call for a response followed by a grant) is probably worth more than half a point in the baseline band, where the pooled rate includes exactly such paths. The document says this itself, so the number is a judgment call rather than an error.
- The upward adjustments (experienced counsel, paid petition, Eleventh Circuit grant share) are mentioned and then dismissed in one sentence; a line on why counsel's reputation does not offset a waiver would have closed the argument.

These are minor. The analysis is sound given the outcome and would have been sound had the Court surprised it. `reasoning_quality` 0.88.

## Leakage

Mode `forward` per the captured log, with every call captured. The prediction was created 2026-09-17 against the 2026-09-16 snapshot; the petition was resolved 2026-10-05. The latest `retrieved_doc_date` in the log is 2026-09-17 on a general corpus query that returned recent SCOTUS rows unrelated to this petition; the CourtListener docket call is dated 2026-05-19 and confirmed the docket was open. One shell call listed the predictor's own earlier prediction on a different case as a template; that is not outcome material. Nothing suggests the case was decided when provisioned. `influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false, `leakage_suspected` = false.

## Big case

My independent read is 0.08: a local quiet-title dispute with a procedural question the Court settled forty years ago, no amicus, a government waiver, and a silent denial.
