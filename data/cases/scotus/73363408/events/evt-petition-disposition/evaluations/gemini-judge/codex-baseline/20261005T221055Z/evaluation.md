# Evaluation

- **Outcome Match:** The outcome was `denied` and the candidate predicted `denied`. `correct` = 1.
- **Brier Score:** With an actual grant of 0 and probability of 0.005, the `brier_score` is 0.000025.
- **Base Rate & Skill:** This is a cert-stage cell. The prediction's context named a `baseline` band under `sal-v4`. Based on the `statpack.md`, the segment base rate pooled over prior Terms (2017-2024) is approximately 5.12% (0.0512). The Brier skill score is ~0.990. The basis is `risk_set`.
- **Reasoning Quality:** 0.9. The predictor's reasoning correctly identified the core vehicle problems—fact-bound nature of the dispute, state procedural hurdles, lack of a square conflict, and waiver of response. The probability adjustment downward was well-reasoned.
- **Leakage:** The prediction was made in `forward` mode, and the event was genuinely unresolved at the time. No outcome material was retrieved.