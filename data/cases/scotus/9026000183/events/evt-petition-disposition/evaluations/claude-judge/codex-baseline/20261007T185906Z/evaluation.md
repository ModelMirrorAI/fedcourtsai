# Evaluation — codex-baseline — scotus/9026000183 / evt-petition-disposition

**Verdict:** disposition correct (`denied` == `denied`), probability 0.12 against a denial. Brier **0.0144**; skill vs the band baseline **-4.714** (negative: the forecast put roughly 2.2–2.6× the risk-set rate on a grant that did not happen, and the Brier penalty of that overshoot exceeds the baseline's own).

## Cell

Cert-stage petition event (`event.yaml` stage `cert`, moment `distribution`), **forward** mode. Outcome: **denied** on 2026-10-05 at the Term's opening order list after a single distribution for the 2026-09-28 conference, with a noted vote ("Justice Kavanaugh would grant") recorded as `noted_dissent_from_denial: true`; `actual_granted` = 0. No CVSG, no relist.

## Baseline

The prediction froze `band: baseline` under `salience_version: sal-v4`, and the committed `metrics/statpack.md` band table heading names sal-v4, so the basis is `risk_set`: the bracketed **reached** figure for `baseline`, pooled resolved-weighted over the rendered Terms strictly before 2026 (2017–2025; the caption renders 10 of 10 Terms, so the rendered window is the pack's whole window and matches the in-code lookback). Pooled from the pack's exact per-Term figures: 638 weighted grants over 12,720 weighted resolved = **0.0502**. Baseline Brier against a denial: 0.00252.

## Reasoning quality: 0.78

A disciplined rationale. The information boundary is stated precisely, the anchor is computed exactly from the pack (638 / 12,720 = 5.02%, matching my own pooling), and the freshness qualification is honest about what the service backend could not report. The upward case is argued from the petition's actual content (common proof versus similar individualized evidence, Judge Willett's reservations, the sequencing plan) and the downward case from the opposition's (uniform unpaid-leave practice distinguishing the cited comparators; alternative common questions of reasonableness and undue hardship; the provisional, modifiable certification order). Judge Willett's concurrence is correctly read as an attention signal, not a dissent. The *Tyson Foods* check is a sensible use of an older authority to test whether the opposition's doctrinal answer is substantial. Weaknesses: the 12% still sits 2.4× the anchor after the candidate's own account of why denial was much likelier, and the rationale does not say which upward factor carries that gap; the hold-then-GVR route via *Detwiler* is given real weight on a posture the candidate admits it did not verify and without noting that *Detwiler* reaches only the sincerity prong. The reasoning is sound, well-sourced to the record, and candid about its limits.

## Leakage

Forward cell (log mode=forward); prediction created 2026-10-04T20:54Z, the denial issued 2026-10-05. Log: 41 calls, coverage 0.90. Captured calls read the prompt, schemas, snapshot 2026-10-04, documents, petition and opposition slices, statpack.md/json, and the git vintage of the statpack. Four `web-search` rows are `unobserved`; their queries are general Rule 10 / Rules of the Court URLs, nothing naming this petition. CourtListener calls: a citation analysis of Wal-Mart, Halliburton and Tyson Foods and a read of the 2016 Tyson Foods opinion. No retrieved_doc_date at or after 2026-10-05, no query for this docket or caption, no `data/qp-topics/` read. The reasoning states an explicit information boundary and no outcome knowledge. No outcome material retrieved.

Grade: `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case

Evaluator read 0.42. Rule 23 commonality/predominance for a Title VII religious-accommodation class of roughly a thousand United employees who refused a COVID-19 vaccine mandate, with the Fifth Circuit's novel three-stage 'class rostering' plan as the concrete target; former Solicitor General as counsel and two trade-association amici. A grant would have reached class-action practice broadly and the setting is newsworthy, but the question is procedural and interlocutory, the Court denied after one conference, and only one Justice noted a would-grant with no written dissent. Mid-range stakes, below the top tier. Formed from the record and outcome; the predictors' big_case_score fields were visible inside prediction.json when I read it, which I note but did not use.

## Not scored here

`claims` and `predicted_reasoning.md` are not graded (the harness scores the claims block in code). No votes scored on a cert cell. Not a merits cell, so no `semantic_grades` block.
