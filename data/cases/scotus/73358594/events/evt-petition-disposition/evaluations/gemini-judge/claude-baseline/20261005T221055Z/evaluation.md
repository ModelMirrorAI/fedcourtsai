# Evaluation for claude-baseline

The prediction correctly forecast a denial with a 1.0% probability (Brier score 0.0001).

**Base rate and skill:** The predictor correctly anchored on the `baseline` salience band under `sal-v4`. Using the risk-set (`reached`) figures pooled across strictly prior Terms (OT2017–OT2024), the baseline grant rate is approximately 5.1%. The Brier skill score against this baseline is strong (0.961).

**Reasoning quality:** Very Good. The rationale correctly interpreted the lack of a government response (waiver) as a strong indicator of denial. The analysis appropriately discounted the petition for being a Rule 36 affirmance and for lacking a circuit split. The adjustments were logical and sound. The manual baseline calculations matched the required methodology.

**Leakage:** The prediction ran in `forward` mode. The captured tool transcript shows MCP courtlistener searches but no retrieval of actual outcome or leaked material. No leakage suspected.
