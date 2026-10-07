# Evaluation of gemini-baseline

**Correctness:** The candidate correctly predicted the disposition as `denied` (P=0.005). The Brier score is 0.000025.

**Reasoning Quality:** The reasoning quality is high (0.8). The predictor accurately identified the underlying case using a web search when CourtListener MCP failed, correctly characterizing it as an unpublished, fact-bound immigration dispute dismissed on jurisdictional grounds (untimeliness). The combination of the SG waiver and the nature of the lower court ruling led to a solid, well-reasoned downward adjustment from the baseline.

**Base Rate Mismatch:** The predicted base rate and skill score were omitted because the prediction utilized the `sal-v3` salience band, while the current `statpack.md` provides base rates based on `sal-v4`.

**Leakage:** The prediction ran in `forward` mode. Although a web search was executed, its retrieval target and date did not expose the Supreme Court's actual resolution.
