# Evaluation for codex-baseline

The candidate predicted `denied` with 0.08 probability. The actual outcome was `withdrawn`.
Since `denied` does not exactly match `withdrawn`, the prediction is scored as incorrect on the categorical axis (`correct: 0`).
The `brier_score` is computed as `(0.08 - 0)**2 = 0.0064`, because a withdrawn disposition counts as 0 (not granted).
This is an `interim` stage cell; `segment_base_rate` and `brier_skill_score` are omitted, and will be stamped by the harness.

## Reasoning Quality
The reasoning quality is scored at 0.9. The candidate accurately recognized the cell as a forward, interim application. It correctly anchored on the pooled interim base rate and adjusted downward based on the specific procedural defects in the case and weak doctrinal grounds. The rationale was thorough and sound given the available information.

## Leakage
The prediction ran in `forward` mode. Retrieval logs and reasoning showed no access to the actual outcome.
