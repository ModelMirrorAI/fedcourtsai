# Evaluation for codex-baseline

**Correctness:** The candidate correctly predicted a denial (`correct` = 1) with a 0.003 probability, resulting in a Brier score of 0.000009.
**Base Rate:** Omitted due to salience version mismatch (`sal-v3` vs `sal-v4` in statpack).
**Reasoning Quality (0.9):** The candidate's legal analysis was robust, specifically distinguishing *Lee v. Kemna* based on the petition's facts, and properly computing the base rate pool over strictly prior terms.
**Leakage:** The prediction was made in forward mode. The retrieval log confirms no retrieval beyond the provisioned inputs.
