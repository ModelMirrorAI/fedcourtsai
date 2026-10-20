# gemini-baseline — evaluation

**Cell.** Cert stage, forward mode. Outcome: `denied` (2026-10-19), `actual_granted` 0, two distributions, no CVSG, no noted dissent from denial. The prediction froze `context.band` = `elevated` under `sal-v4`, so the base-rate anchor, its basis and the skill score are the harness's risk-set stamp; I leave them null and quote no rate of my own (see "the stamped segment base rate"). `claim_scores` is the harness's too. No semantic set is declared on a cert cell, so there is no `semantic_grades` block.

**Score.** Predicted `denied` at P(grant) = 0.45 → correct = 1, Brier = 0.2025. The label is right, but the probability sits close to a coin flip and the Brier is the weakest of the three.

**Reasoning quality: 0.40.** Short and one-sided. It cites the band anchor loosely ("roughly 14% to 20%") and then nearly triples it on two signals: the requested response and the amicus count. Its count of six amicus briefs conflicts with the seven the other analyses enumerate from the record. Calling the 4-3 decision below a "clean, high-stakes Due Process question" overlooks the respondents' central waiver/adequate-state-ground argument. It gestures at "state-law vehicle issues" only in passing, without engaging the BIO, the disputed split, or the fact-bound kinship and fraud findings. Those are exactly the factors that most plausibly explain a quiet denial with no noted dissent. Its stated reason for landing just under 50% ("plenary review remains the exception") is a nod to the base rate, not an argument for 0.45. Salience is treated as cert-worthiness throughout.

**Leakage.** Forward; `not_applicable`. One corpus query bounded before the prediction date; no web or MCP retrieval. The log's result capture is 0.0, so I graded the call on its query.
