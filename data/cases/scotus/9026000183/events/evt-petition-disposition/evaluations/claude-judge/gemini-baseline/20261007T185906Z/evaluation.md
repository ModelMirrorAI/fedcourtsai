# Evaluation — gemini-baseline — scotus/9026000183 / evt-petition-disposition

**Verdict:** disposition correct (`denied` == `denied`), probability 0.11 against a denial. Brier **0.0121**; skill vs the band baseline **-3.801** (negative: the forecast put roughly 2.2–2.6× the risk-set rate on a grant that did not happen, and the Brier penalty of that overshoot exceeds the baseline's own).

## Cell

Cert-stage petition event (`event.yaml` stage `cert`, moment `distribution`), **forward** mode. Outcome: **denied** on 2026-10-05 at the Term's opening order list after a single distribution for the 2026-09-28 conference, with a noted vote ("Justice Kavanaugh would grant") recorded as `noted_dissent_from_denial: true`; `actual_granted` = 0. No CVSG, no relist.

## Baseline

The prediction froze `band: baseline` under `salience_version: sal-v4`, and the committed `metrics/statpack.md` band table heading names sal-v4, so the basis is `risk_set`: the bracketed **reached** figure for `baseline`, pooled resolved-weighted over the rendered Terms strictly before 2026 (2017–2025; the caption renders 10 of 10 Terms, so the rendered window is the pack's whole window and matches the in-code lookback). Pooled from the pack's exact per-Term figures: 638 weighted grants over 12,720 weighted resolved = **0.0502**. Baseline Brier against a denial: 0.00252.

## Reasoning quality: 0.48

A short rationale that gets the frame right and stops there. It names the correct band and a rough risk-set rate ("roughly 4-6%") rather than pooling the table, then adjusts upward on three surface signals: elite counsel, two business amici, and the Court's appetite for Rule 23 policing after *Wal-Mart*. The restraint argument (first conference, most petitions denied) is sound and is what kept the number lowest of the three. What is missing is any engagement with the adversarial record: the retrieval log shows the questions presented, snapshot and manifest were read but not the petition or the brief in opposition, so the rationale never tests the asserted split, never meets the opposition's uniform-policy answer, and never weighs the interlocutory abuse-of-discretion posture that the outcome suggests mattered. The stated "main uncertainty" (whether the Fifth Circuit's denial of en banc review is a clean vehicle) is muddled: en banc denial is not itself a vehicle problem. The relist and CVSG rationales are one sentence each but directionally right. Credit for a correctly bounded prior and honest disclosure that the corpus query failed; the deduction is for analysis that is thin relative to what was provisioned.

## Leakage

Forward cell (log mode=forward); prediction created 2026-10-04T20:25Z, the denial issued 2026-10-05. Log: 31 calls, every result marker `unobserved` (coverage 0.0, the engine's standing shape), so each call is graded on its query: reads of the prompt, context, event, documents manifest, snapshot 2026-10-04, questions presented, statpack and schema; one corpus `query` for Rule 23 priors with `--decided-before 2026`, which the candidate's retrieval.md says failed on an argument error; no web search, no CourtListener call, no docket-caption or disposition query, no `data/qp-topics/` read. Reasoning reads only pre-conference facts. No outcome material retrieved; nothing to suggest a decided case was provisioned forward.

Grade: `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case

Evaluator read 0.42. Rule 23 commonality/predominance for a Title VII religious-accommodation class of roughly a thousand United employees who refused a COVID-19 vaccine mandate, with the Fifth Circuit's novel three-stage 'class rostering' plan as the concrete target; former Solicitor General as counsel and two trade-association amici. A grant would have reached class-action practice broadly and the setting is newsworthy, but the question is procedural and interlocutory, the Court denied after one conference, and only one Justice noted a would-grant with no written dissent. Mid-range stakes, below the top tier. Formed from the record and outcome; the predictors' big_case_score fields were visible inside prediction.json when I read it, which I note but did not use.

## Not scored here

`claims` and `predicted_reasoning.md` are not graded (the harness scores the claims block in code). No votes scored on a cert cell. Not a merits cell, so no `semantic_grades` block.
