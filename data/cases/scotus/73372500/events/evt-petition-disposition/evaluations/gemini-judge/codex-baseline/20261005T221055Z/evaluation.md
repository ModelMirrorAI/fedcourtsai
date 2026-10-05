# Evaluation for codex-baseline

- **Outcome**: The petition was denied. The predictor correctly forecasted `denied` with a probability of 0.025. `correct` is 1.
- **Base Rate & Skill**: The prediction provided a `context.band` of `baseline` and `context.salience_version` of `sal-v4`. This is a cert stage event. Pooling the strictly-prior terms (OT2017 to OT2024), the `baseline` segment base rate (`risk_set`) is 5.12%. With an actual outcome of 0, the skill score over the baseline is 0.762.
- **Leakage**: The prediction mode was `forward`. The retrieval log shows no retrieval of any information past the cutoff date that revealed the outcome. `influenced_prediction` is `not_applicable`.
- **Reasoning**: Solid reasoning. The predictor successfully identified the vehicle problems (unpublished order declining original jurisdiction) and appropriately discounted the grant probability relative to the baseline base rate.
- **Semantic Grades**: Not applicable on a cert-stage cell.
