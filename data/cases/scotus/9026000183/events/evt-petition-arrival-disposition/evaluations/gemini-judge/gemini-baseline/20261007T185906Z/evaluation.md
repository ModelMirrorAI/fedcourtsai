# Evaluation for gemini-baseline

The cell is a cert event. The outcome was "denied", and the candidate predicted "denied" with P(grant/GVR) = 0.28.
The Brier score is 0.0784 and the prediction is correct.

`segment_base_rate` and `brier_skill_score` are omitted, and `base_rate_basis` is null. This is because there is a salience-version mismatch: the prediction froze a band under `sal-v3`, while the committed `statpack.md` provides base rates under `sal-v4`. Per the evaluation rules, the base rate from a different salience version cannot be applied.

The reasoning quality is evaluated at 0.8. The predictor correctly assessed the procedural posture of the case, identifying the *Detwiler* hold request as well as a circuit split, and arrived at a well-reasoned upward adjustment from the base rate while keeping the probability below 50% due to potential issues that might lead to a denial.

The prediction was made in forward mode. The log shows no retrieval of material postdating the prediction date. No leakage is suspected.
