# Evaluation — codex-baseline — Sanders v. City of Long Beach (scotus/73272489, evt-petition-disposition)

## Outcome and scores

Cert-stage cell. The petition (No. 25-1235, paid, pro se) was distributed once, for the September 28, 2026 long conference, and **denied on October 5, 2026** with no response called for and no noted dissent (`outcome.json`: `actual_disposition` = `denied`, `actual_granted` = 0, `distribution_count` = 1).

- `correct` = 1: `predicted_disposition` = `denied` matches.
- `brier_score` = (0.003 − 0)² = 0.000009.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze `band` = `baseline` with `salience_version` = `sal-v4` and `term` = 2025; the committed `metrics/statpack.md` band table is headed `sal-v4`, so the versions match. I pooled the bracketed `reached` figure for `baseline`, resolved-weighted, over every rendered Term strictly before 2025 (2017–2024, eight rows, weighted n = 11,580), which gives 5.12%. The caption states the table renders 10 of 10 Terms, so the rendered window is the pack's whole window and no window divergence needs flagging; the in-code ten-Term lookback would reach 2015, but the pack holds nothing before 2017, so the two windows coincide. The pooled figure is built from the table's rounded percentages, so it is approximate at the third decimal.
- `brier_skill_score` = 1 − 0.000009 / 0.0512² ≈ 0.9966.
- No `vote_accuracy` (cert cell; the empty vote block is correct and is never scored here). No `semantic_grades` (no semantic set is declared on a cert cell, and `semantic_claims` is null). `claim_scores` is the harness's.

## Reasoning quality: 0.85

What drove the score. The rationale is the most carefully reasoned of the three. It identifies the right anchor (the sal-v4 baseline bracketed reached rate pooled over 2017–2024, computed and stated as approximate), explains the downward adjustment on substance rather than on the petitioner's pro se status alone, and names the specific vehicle problems: a grievance-style question presented with no identified conflict, a mix of state tort authority, Federal Rules, and criminal impeachment doctrine that does not establish a federal question in a state civil trial, an unpublished opinion, and the appellate court's record-citation criticism that the petition itself acknowledges. It is disciplined about epistemic status: it marks the trial-court narrative as the petitioner's account, does not infer a waiver from the absence of a response, and declines to assert an independent state ground it cannot see without the opinion. The retention of a small residual probability is justified rather than reflexive, and the forecast of denial without writing at the first conference is exactly what happened.

Minor deductions. The document is longer than its content needs, and a fair amount of it is procedural self-narration (the uv cache, the failed Rule 10 fetch) that belongs in the retrieval note rather than the rationale. It uses the originating-court context only in passing and does not engage the Cal. Ct. App. cut the statpack carries, which would have sharpened the vehicle read. None of this affects the soundness of the legal analysis given the outcome.

## Leakage

Mode `forward`. The prediction was written on 2026-09-16, twelve days before the conference and nineteen before the denial, so the case was genuinely open. The harness log shows 27 calls: local reads of the prompt, schemas, provisioned snapshot and petition, and the committed statpack; two `web-search` rows marked `unobserved` whose queries concern only Supreme Court Rule 10 and the rules PDF, naming no case; and a shell fetch of the same PDF that returned 404. No call carries a `retrieved_doc_date`, none names this docket or caption externally, and none reads `data/qp-topics/`. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The predictor's own retrieval note disclosed the same attempts, which counts for the cell's integrity. Nothing suggests a decided case was provisioned forward: the snapshot's last entry was the June 17 distribution.

## Big case

My own read is 0.02. A single homeowner's state-law dangerous-condition claim against one city, decided on evidentiary and credibility rulings, affirmed unpublished, with federal hooks that do not reach a state civil trial, no amicus, no response, and a silent first-conference denial. The predictor's own `big_case_score` sits in the staged `prediction.json`, so I could not avoid seeing it before writing; my figure was formed from the record and the outcome rather than from that number, and I supply no agreement figure.
