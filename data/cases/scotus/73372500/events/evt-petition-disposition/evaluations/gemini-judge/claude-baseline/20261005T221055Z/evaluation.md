# Evaluation for claude-baseline

- **Outcome**: The petition was denied. The predictor correctly forecasted `denied` with a probability of 0.006. `correct` is 1.
- **Base Rate & Skill**: The prediction provided a `context.band` of `baseline` and `context.salience_version` of `sal-v4`. This is a cert stage event. Pooling the strictly-prior terms (OT2017 to OT2024), the `baseline` segment base rate (`risk_set`) is 5.12%. With an actual outcome of 0, the skill score over the baseline is 0.986.
- **Leakage**: The prediction mode was `forward`. The predictor retrieved a supplemental brief filed prior to the event resolution, which is permitted in forward mode as it predates the outcome. The retrieval log shows no retrieval of any information that revealed the outcome itself. `influenced_prediction` is `not_applicable`.
- **Reasoning**: Outstanding and detailed reasoning. The predictor accurately assessed the baseline, recognized the independent and adequate state ground issue, identified the lack of split match for a neighborhood organization vs an owner, and identified the significance of the waiver.
- **Semantic Grades**: Not applicable on a cert-stage cell.
