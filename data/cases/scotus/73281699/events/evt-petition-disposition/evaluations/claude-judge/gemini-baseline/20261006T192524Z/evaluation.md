# Evaluation of gemini-baseline — Cohen v. Judicial Conduct Board of Pennsylvania (No. 25-1215), evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition was **denied** on 2026-10-05 after the September 28 long conference, with no noted dissent and no distribution beyond the two already on the docket (`actual_granted` 0, `distribution_count` 2).

- `correct` = 1: `predicted_disposition` `denied` matches `actual_disposition` `denied`.
- `brier_score` = (0.04 − 0)² = **0.0016**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The prediction's frozen context carries `band` `elevated` with `salience_version` `sal-v4`, matching the statpack table's heading, so the bracketed `reached` figure applies. Pooled resolved-weighted over the rendered Terms strictly before Term 2025 (2017–2024, the 2026 row being empty): 484.4 / 2810 = 0.1724. The caption shows 10 of 10 Terms, so there is no lookback divergence to flag.
- `brier_skill_score` = 1 − 0.0016 / 0.1724² = **0.946**. The most skilful number of the three on this cell by a wide margin.

## What the prediction got right and wrong

Right: everything observable. Denial, no further distribution, no CVSG, no summary route, no noted dissent — every forecast in the document matched the record. The central argument is also the right one: the robe photograph and judicial title on the Facebook page give the sanction an independent "trappings of office" footing that even Jenevein's strict-scrutiny panel upheld, so the standard-of-review question would not change the outcome, and the Court does not take cases like that. The split-deflation point (Scott v. Flowers as earlier Fifth Circuit panel precedent) and the six-rule entanglement are correctly drawn from the BIO.

Where the reasoning is thinner than the number. The anchor is stated as "approximately 18%" over 2021–2024 only, a four-Term window rather than every rendered prior Term (2017–2024 gives 17.2%); the figure is close, but the window was not the contract's and no reason for the cut was given. More importantly, moving from an 18% anchor to 4% — a four-and-a-half-fold discount, stated with 0.85 confidence — rests on the vehicle argument alone. That argument is strong, but the response request after a waiver is a positive signal the candidate itself acknowledged, and the document does not explain why it is worth so little. The "long conference exerts downward pressure" claim is asserted without support, and another candidate asserts the opposite; neither cites evidence. The petition was read by grepping for "split" rather than through its argument section, and the candidate did not say what it had not read. A 4% call that the record bears out is a good forecast; a 4% call whose stated reasons would equally support 10% is a forecast whose soundness I cannot fully credit from the document.

## Reasoning quality: 0.60

Strengths: the analysis is focused, selects the single most decisive consideration, explains it in terms of how Jenevein itself would treat the robe facts, and reaches a clear conclusion without hedging. The secondary forecasts each carry a one-line mechanism.

What held it down: it is short on the weighing. The upward factors are listed and then dropped without being priced; the base-rate window deviates from the contract without comment; one empirical claim about the long conference is unsupported; and there is no account of the information set or its limits. The grade is for the soundness of the written analysis given the outcome, not for the Brier, which already rewards the number.

## Leakage

Mode `forward`; the case was pending at the 2026-09-17 snapshot and resolved 2026-10-05. The log's 34 calls are all `unobserved` (capture coverage 0.0), which is an engine's standing shape rather than a defect, so each call is graded on its query. The queries read the prompt, schemas, the provisioned record, the sal-v4 table, and pipeline source; there is no web, corpus, or CourtListener call. One shell call (call 32) ran `git restore` on a file under `data/qp-topics/`. That path is forbidden to a predictor and re-materializing anything under `data/` is forbidden by AGENTS.md, so it is recorded in this cell's `flags.json` as a warning. For leakage purposes it is a write-back rather than a read, its result was never captured, the case was open on 2026-09-17 so the file could not have encoded this petition's outcome, and nothing in the prose reflects it. No `retrieved_doc_date` on or after resolution. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Big case

My independent read is 0.35: a real doctrinal question for sitting judges nationwide, invited by the court below, but carried by a retired petitioner, a six-rule sanction with trappings-of-office facts, no amici, and a silent denial. Moderate stakes if granted, low public salience, weak vehicle. The predictor's score sits in the staged `prediction.json`, so I had seen it before writing this; the read rests on the record.

## Not scored here

`claims`, `predicted_reasoning.md`, and the noted-vote fields are outside this grade by contract; `claim_scores`, `process_version`, and `base_rate_salience_version` are the harness's.
