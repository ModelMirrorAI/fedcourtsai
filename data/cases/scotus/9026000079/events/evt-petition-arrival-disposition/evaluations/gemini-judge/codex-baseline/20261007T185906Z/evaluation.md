# Evaluation of codex-baseline

**Correctness:** The candidate correctly predicted the disposition as `denied` (P=0.05). The Brier score is 0.0025.

**Reasoning Quality:** The reasoning quality is fair (0.6). The predictor anchored well on the salience-band baseline and successfully used the statpack numbers. However, they did not investigate the case details effectively when their CourtListener search failed, leading to a bare anchor without the strong downward adjustments that case facts supported (unpublished, untimely).

**Base Rate Mismatch:** The predicted base rate and skill score were omitted because the prediction utilized the `sal-v3` salience band, while the current `statpack.md` provides base rates based on `sal-v4`.

**Leakage:** The prediction ran in `forward` mode. No web search or courtlistener queries reached the case outcome, confirming it was free from leakage.
