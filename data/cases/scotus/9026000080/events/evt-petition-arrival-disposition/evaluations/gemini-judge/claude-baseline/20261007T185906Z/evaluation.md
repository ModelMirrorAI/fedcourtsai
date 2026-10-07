# Evaluation of claude-baseline

**Prediction Correctness**: The candidate correctly predicted a "denied" disposition (`correct` = 1).
**Brier Score**: With a predicted probability of 0.004 for a grant and an actual grant outcome of 0, the Brier score is 0.000016.

**Base Rates**: The prediction anchored to a `sal-v3` salience band, but the `statpack.md` provides base rates only for `sal-v4`. Because of this version mismatch, `segment_base_rate` and `brier_skill_score` are omitted, and `base_rate_basis` is recorded as `null` in accordance with the evaluation rules.

**Reasoning Quality**: The reasoning earns a 0.9 `reasoning_quality`. The candidate produced an exceptionally detailed and convincing assessment of the baseline probability, correctly diagnosing all significant negative indicators such as pro-se status, waived response, thin vehicle, and pure error correction requests. It also correctly evaluated the single positive indicator (the Fifth Circuit dissent). The probability was accurately discounted based on the petition's specifics.

**Leakage**: The prediction ran in `forward` mode. The retrieval log reflects only valid baseline analysis and tool calls (like reading local schemas, statpack.md, querying the corpus, and doing a courtlistener search). All retrieved dates are well before the resolution date, confirming no outcome-revealing material was seen.
