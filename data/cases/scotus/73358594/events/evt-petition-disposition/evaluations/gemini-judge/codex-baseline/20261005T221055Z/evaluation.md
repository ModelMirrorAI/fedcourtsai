# Evaluation for codex-baseline

The prediction correctly forecast a denial with a 1.5% probability (Brier score 0.000225). 

**Base rate and skill:** The predictor correctly anchored on the `baseline` salience band under `sal-v4`. Using the risk-set (`reached`) figures pooled across strictly prior Terms (OT2017–OT2024), the baseline grant rate is approximately 5.1%. The Brier skill score against this baseline is strong (0.914).

**Reasoning quality:** Excellent. The rationale demonstrates a sound reading of the record, noticing that the government had waived its response and the lower court decision was a non-precedential Rule 36 affirmance. The predictor properly analyzed the substantive issues (whether the MSPB had to consider the secondary whistleblower category) and noted the factbound nature of the error correction posture. The base-rate derivation was explicitly calculated and correct.

**Leakage:** The prediction ran in `forward` mode. The captured tool transcript confirms no post-decision material was retrieved, preserving the forward baseline. No leakage suspected.
