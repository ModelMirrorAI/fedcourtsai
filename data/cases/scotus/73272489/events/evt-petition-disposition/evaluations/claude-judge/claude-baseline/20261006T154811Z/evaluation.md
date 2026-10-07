# Evaluation — claude-baseline — Sanders v. City of Long Beach (scotus/73272489, evt-petition-disposition)

## Outcome and scores

Cert-stage cell. The petition (No. 25-1235, paid, pro se) was distributed once, for the September 28, 2026 long conference, and **denied on October 5, 2026** with no response called for and no noted dissent (`outcome.json`: `actual_disposition` = `denied`, `actual_granted` = 0, `distribution_count` = 1).

- `correct` = 1: `predicted_disposition` = `denied` matches.
- `brier_score` = (0.005 − 0)² = 0.000025.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze `band` = `baseline` with `salience_version` = `sal-v4` and `term` = 2025; the committed `metrics/statpack.md` band table is headed `sal-v4`, so the versions match. I pooled the bracketed `reached` figure for `baseline`, resolved-weighted, over every rendered Term strictly before 2025 (2017–2024, eight rows, weighted n = 11,580), which gives 5.12%. The caption states the table renders 10 of 10 Terms, so the rendered window is the pack's whole window and no window divergence needs flagging; the in-code ten-Term lookback would reach 2015, but the pack holds nothing before 2017, so the two windows coincide. The pooled figure is built from the table's rounded percentages, so it is approximate at the third decimal.
- `brier_skill_score` = 1 − 0.000025 / 0.0512² ≈ 0.9905.
- No `vote_accuracy` (cert cell; the empty vote block is correct and is never scored here). No `semantic_grades` (no semantic set is declared on a cert cell, and `semantic_claims` is null). `claim_scores` is the harness's.

## Reasoning quality: 0.82

What drove the score. The rationale is tight and legally specific. It takes the correct anchor (the sal-v4 baseline bracketed reached rate pooled over 2017–2024, about 5.1% over roughly 11,600) and then gives concrete, accurate reasons the petition sits far below it: the Federal Rules of Evidence and Civil Procedure do not govern a California trial, the Sixth Amendment confrontation right has no application in a civil case, the question presented is a narrative of grievances rather than a legal question, the opinion below is unpublished, and no split is alleged. It makes good use of the statpack's originating-court cut for the Second Appellate District and correctly reads the first-conference posture (one distribution, no response called for) as the shape of a petition denied without comment. It states a defensible range and explains why it does not go lower. The forecast matched the outcome in every particular.

Deductions. Two points are asserted more confidently than the provisioned record supports. The rationale states that the claim rests on "an adequate and independent state ground" as a finding, when neither the opinion nor the appendix was provisioned; the better-calibrated reading, which the stronger candidate gave, is that the acknowledged record-citation criticism is a vehicle risk whose exact shape is unknown. The explanation that the Second District's GVR share "is driven by criminal petitions held for intervening decisions" is plausible but offered without any check. The reading of "no waiver" as a negative signal is also slightly off: before the Court calls for a response, a respondent's silence is the ordinary state and tells little either way. These are calibration-of-confidence issues inside a sound analysis, not errors of direction.

## Leakage

Mode `forward`. The prediction was written on 2026-09-16, twelve days before the conference and nineteen before the denial, so the case was genuinely open. The harness log shows 23 calls with full result capture: local reads of the prompt, provisioned snapshot and petition, statpack and schema; two corpus queries over denied and granted 2020s SCOTUS rows (generic population lookups, not this case; the single `retrieved_doc_date`, 2025-02-11, predates the event and belongs to a returned prior); and one CourtListener `docket-entries` call for this docket on 2026-09-16 that returned 0 rows, before resolution. A `git status` call pipes through a filter that excludes `data/qp-topics` paths rather than reading them. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The predictor's retrieval note disclosed every lookup, which counts for the cell's integrity. Nothing suggests a decided case was provisioned forward.

## Big case

My own read is 0.02. A single homeowner's state-law dangerous-condition claim against one city, decided on evidentiary and credibility rulings, affirmed unpublished, with federal hooks that do not reach a state civil trial, no amicus, no response, and a silent first-conference denial. The predictor's own `big_case_score` sits in the staged `prediction.json`, so I could not avoid seeing it before writing; my figure was formed from the record and the outcome rather than from that number, and I supply no agreement figure.
