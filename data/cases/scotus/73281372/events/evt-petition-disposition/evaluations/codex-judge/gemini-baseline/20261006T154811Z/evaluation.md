# Evaluation: gemini-baseline

## Result and reasoning quality

- Exact disposition match: **1**.
- Brier: **0.0009** = 0.03 squared.
- Brier skill against the risk-set baseline: **0.6567108291485383**. On this denial, the forecast beats the approximately 5.12% baseline on squared error. This is a single-event comparison, not an estimate of general predictive skill.
- Reasoning quality: **0.56**.

The concise rationale identifies the relevant safe-harbor/extraterritoriality subject and the contested nature of the asserted circuit conflict. It appropriately keeps the large financial stakes distinct from a prediction that review is likely. Its denial forecast is correct.

The analysis is nonetheless thin on the decisive distinctions. It does not develop Section 561(d)'s Chapter 15 role, the difference between available foreign avoidance powers and safe-harbor limitations, or the opposition's alternative-ground and vehicle arguments. The captured queries show reads limited to the petition's first 100 lines and opposition's first 150 lines, not their main argument sections; because results are unobserved, those queries establish attempted scope rather than the contents actually returned. The statement that documents were available does not demonstrate close engagement with those arguments.

Calibration is also underexplained: the rationale takes one prior Term's 5.7% reached figure rather than pooling all displayed eligible Terms, and treats the approximately 1.7% zero-terminal-relist rate as informative about a petition merely at its first distribution. A petition that has not yet relisted can still relist, so the terminal bucket is not the current risk set. The downward movement to 3% is therefore less well-grounded than its favorable realized Brier suggests. The qualitative grade does not reward the smallest grant probability simply because denial occurred and does not score the forecast document or the claims block.

## Scoring basis

The cert-stage outcome records `denied`, `actual_granted = 0`, resolved October 5, 2026. Correctness is the exact disposition match; Brier is the squared grant probability. The outcome supplies no explanation for denial, so agreement with denial does not establish that the Court adopted any particular vehicle or statutory argument.

All baseline calculations use this candidate's frozen `context`: Term 2025, `baseline`, `sal-v4`, matching the committed `metrics/statpack.md` heading. The risk-set baseline pools the bracketed reached figures for every displayed strictly-prior Term, OT2017–OT2024. In descending Term order, the rate/weighted-denominator pairs are 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643. The displayed-rate weighted numerator is 592.925 and denominator is 11,580, giving **0.05120250431778929**. That numerator is an approximation from rounded published percentages, not an integer count. The table renders all 10 of its 10 Terms; OT2025 and OT2026 are excluded. There is no rendered-window divergence or salience-version mismatch. These are the supplied committed pack's denial-reweighted live/historical-slice estimates, not a refreshed corpus measurement.

The forecast document was read for context only. Neither it nor the mechanical claims block enters reasoning quality; claim scores are reserved for the harness. Cert votes are not scored, and this stage declares no semantic set, so vote accuracy, judgment correctness, and semantic grades are omitted. No independent big-case score is supplied.

## Leakage assessment

Forward log, captured-result coverage 0.0: all call results are unobserved, not demonstrated empty or failed. September 16 calls precede the October 5 resolution. Queries target provisioned inputs, statistical context, and general extraterritoriality authorities; no query seeks this petition’s disposition. Reasoning does not presuppose denial as an accomplished fact. The retrieval note’s reported search results and failed corpus lookup are self-reports, not independently verified result contents. No affirmative indication of a decided case being provisioned forward.

Assessment: `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. This is the forward-mode assessment on the available evidence, not a claim that a missing document date or missing result proves absence.
