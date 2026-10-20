# Evaluation — gemini-baseline (cert, forward)

**Outcome:** denied on 2026-10-19 after two distributions, with no noted dissent. **Prediction:** denied, P(grant) = 0.03. Correct; Brier 0.0009, the best of the three.

The prediction froze band `elevated` (`sal-v4`), so the harness writes the segment base rate and skill score at the stamp. I leave both null.

**Reasoning quality 0.45.** The direction is right and the main factors are named: no split, the California Supreme Court denied review, and the claims are weak against a state restructuring its own public institution. But `reasoning.md` is one paragraph. Problems:
- It does not engage the actual cert-stage obstacles in the briefs: the forfeiture of the damages theory, the standing objection, and the dispute over whether the statute contains a contract at all.
- It asserts that the claims are "exceedingly weak" rather than showing it.
- It goes from the ~17% band anchor to 3% with no stated weighting, and it treats the call for response after a waiver as near-neutral.

The low number paid off here. But the analysis behind it is thin, and the reasoning score grades the analysis, not the luck of the realized Brier.

**Leakage:** none. Forward mode. Every call is unobserved (coverage 0.0), so I graded on the queries: all are local reads of the provisioned record and the statpack, with no external retrieval.
