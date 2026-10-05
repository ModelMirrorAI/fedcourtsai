# Evaluation

- **Outcome Match:** The outcome was `denied` and the candidate predicted `denied`. `correct` = 1.
- **Brier Score:** With an actual grant of 0 and probability of 0.001, the `brier_score` is 0.000001.
- **Base Rate & Skill:** This is a cert-stage cell. The prediction's context named a `baseline` band under `sal-v4`. Based on the `statpack.md`, the segment base rate pooled over prior Terms (2017-2024) is approximately 5.12% (0.0512). The Brier skill score is ~1.000. The basis is `risk_set`. Note that the predictor mentioned a 3.9% rate which matches the terminal rate for 2025, but the evaluator calculation correctly pools over prior terms.
- **Reasoning Quality:** 0.9. The predictor recognized the petition as a fact-bound pro se petition challenging a state procedural dismissal with no response filed, heavily discounting the baseline rate.
- **Leakage:** The prediction was made in `forward` mode, and the event was genuinely unresolved at the time.