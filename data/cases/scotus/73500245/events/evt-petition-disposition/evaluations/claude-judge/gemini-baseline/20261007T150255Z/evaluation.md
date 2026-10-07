# Evaluation — gemini-baseline, scotus/73500245, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition in *Blevins v. Alabama State Bar*, No. 25-1344, was distributed once (July 8, 2026, for the September 28, 2026 conference) and **denied on October 5, 2026** without a noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 1).

- `predicted_disposition` denied vs actual denied → **correct = 1**.
- `probability` 0.002 → **brier_score = 0.000004**.
- Base rate: the prediction's frozen context carries `band: baseline` and `salience_version: sal-v4`; the statpack's "Segment base rate by salience band (sal-v4)" heading matches, so the basis is **risk_set**. Pooling the bracketed `reached` figure, resolved-weighted, over every rendered Term strictly before this case's Term 2025 (OT2017–OT2024; the table renders 10 of 10 Terms) gives 593 / 11,580 = **0.0512**. The in-code ten-Term lookback would reach OT2015, but the pack holds nothing before OT2017, so the windows coincide.
- `brier_skill_score` = 1 − 0.000004 / (0.0512 − 0)² = **0.998**.

## Reasoning quality: 0.50

The rationale is a single paragraph. What it says is directionally right: it names the correct band and the roughly 5% baseline rate, it identifies the respondent's July 1 waiver and the fact-bound, local character of a state bar disciplinary challenge, and it correctly notes the Court's practice of calling for a response before granting a waived petition. Those are the two most important signals in this record, and the outcome bore them out.

But the document is a sketch rather than an analysis. It never engages the petition's actual legal theory (the *Marks* fair-notice argument via *Brooks*), says nothing about whether a federal question was preserved (the petition itself discloses the theory first appeared in a reply brief), and does not look at the decision below. The adjustment from ~5% to 0.2% — a factor of twenty-five — rests on two sentences, and one of them overclaims: a waiver is a routine respondent's choice on a petition the respondent reads as weak, not a "definitive signal," and the Court's call-for-response practice makes it a timing signal more than a merits one. The move also leaves no room for uncertainty the candidate had not resolved; nothing in the write-up acknowledges what would have to be true for the number to be wrong. The result is a well-calibrated number supported by a thin argument; `reasoning_quality` grades the argument. A sound write-up that reached the same number with the same evidence would have said why the fair-notice theory does not travel to this setting, or at least that the candidate had not checked.

## Leakage

Mode `forward`. The prediction was written September 18, 2026, before the first conference (September 28) and the denial (October 5), so no outcome existed to leak. The log (22 calls) has `result_capture_coverage` 0.0 — every call is `unobserved`, which is this engine's standing telemetry shape and not a defect — so each call is graded on its query: file reads of the prompt, AGENTS.md, context.json, event.yaml, the 2026-09-17 snapshot, documents.json and the QP; a grep of the statpack band table; the output writes and a validate run. No web, CourtListener or corpus call, no `data/qp-topics/` read, no query naming this docket's disposition. The candidate's `retrieval.md` says the same. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case

My independent read is 0.04: one attorney's 180-day suspension, a state-law-framed QP with a thin federal hook, no split, no amici, waived response, routine first-list denial. The candidate's `big_case_score` was visible in the staged `prediction.json` I read for the context block, so strict pre-exposure independence could not be kept; the read rests on the record and the outcome.

## Not graded here

The claims block and `predicted_reasoning.md` are harness-scored or unscored by contract. No semantic set is declared on a cert cell, so no `semantic_grades` block is written. `vote_accuracy` is omitted on a cert cell.
