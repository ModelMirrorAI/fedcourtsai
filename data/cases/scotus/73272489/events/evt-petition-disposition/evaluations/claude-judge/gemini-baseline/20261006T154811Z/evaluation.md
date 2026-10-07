# Evaluation — gemini-baseline — Sanders v. City of Long Beach (scotus/73272489, evt-petition-disposition)

## Outcome and scores

Cert-stage cell. The petition (No. 25-1235, paid, pro se) was distributed once, for the September 28, 2026 long conference, and **denied on October 5, 2026** with no response called for and no noted dissent (`outcome.json`: `actual_disposition` = `denied`, `actual_granted` = 0, `distribution_count` = 1).

- `correct` = 1: `predicted_disposition` = `denied` matches.
- `brier_score` = (0.001 − 0)² = 0.000001.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze `band` = `baseline` with `salience_version` = `sal-v4` and `term` = 2025; the committed `metrics/statpack.md` band table is headed `sal-v4`, so the versions match. I pooled the bracketed `reached` figure for `baseline`, resolved-weighted, over every rendered Term strictly before 2025 (2017–2024, eight rows, weighted n = 11,580), which gives 5.12%. The caption states the table renders 10 of 10 Terms, so the rendered window is the pack's whole window and no window divergence needs flagging; the in-code ten-Term lookback would reach 2015, but the pack holds nothing before 2017, so the two windows coincide. The pooled figure is built from the table's rounded percentages, so it is approximate at the third decimal.
- `brier_skill_score` = 1 − 0.000001 / 0.0512² ≈ 0.9996.
- No `vote_accuracy` (cert cell; the empty vote block is correct and is never scored here). No `semantic_grades` (no semantic set is declared on a cert cell, and `semantic_claims` is null). `claim_scores` is the harness's.

## Reasoning quality: 0.50

What drove the score. The direction and the conclusion are right, and the core observation is correct: a fact-bound state evidentiary and judicial-bias grievance, framed as due process, with no split and no important federal question, is denied almost as a matter of course. The forecast of a first-conference denial with no writing was borne out. The best Brier of the three is a consequence of that correct direction, but the quality score grades the analysis, not the number.

Deductions, and they are substantial. The anchor is taken from the single 2024 Term row (5.7%) rather than pooled over the prior Terms the prompt and the statpack caption call for; the numerical effect is small here, but it is the wrong procedure and would matter in a band with more Term-to-Term variance. The rationale is one paragraph and does not engage the petition itself: the harness log shows it read `questions-presented.txt` but never the 24-page `petition.txt`, so the vehicle analysis rests on a single garbled question and the docket shell. It does not say why the Federal Rules and Sixth Amendment hooks fail, does not consider the unpublished-opinion or record-citation problems, and does not explain how "adjusted downward significantly to practically zero" arrives at 0.001 rather than 0.005 or 0.0005. It also calls the petition "paid" from the snapshot, which is correct, but offers nothing on what a paid pro se filing signals. The outcome vindicates the call, not the depth of the work behind it.

## Leakage

Mode `forward`. The prediction was written on 2026-09-16, twelve days before the conference and nineteen before the denial, so the case was genuinely open. The harness log shows 23 calls, every one marked `unobserved` (`result_capture_coverage` 0.0, which is this engine's standing telemetry shape, not a defect), so each is graded on its query: file reads of AGENTS.md, the prompt, `event.yaml`, `context.json`, the snapshot, `documents.json`, `questions-presented.txt`, the statpack band table and the schema; writes to its own cell; and a `validate` run. No web, MCP, or corpus call; nothing names this case externally; nothing reads `data/qp-topics/`. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. Its retrieval note says "No retrieval beyond the provisioned inputs," which the log bears out. Nothing suggests a decided case was provisioned forward.

## Big case

My own read is 0.02. A single homeowner's state-law dangerous-condition claim against one city, decided on evidentiary and credibility rulings, affirmed unpublished, with federal hooks that do not reach a state civil trial, no amicus, no response, and a silent first-conference denial. The predictor's own `big_case_score` sits in the staged `prediction.json`, so I could not avoid seeing it before writing; my figure was formed from the record and the outcome rather than from that number, and I supply no agreement figure.
