# Evaluation — codex-baseline (cert, forward)

**Outcome:** denied on 2026-10-19 after two distributions, with no noted dissent. **Prediction:** denied, P(grant) = 0.08. Correct; Brier 0.0064.

The prediction froze band `elevated` (`sal-v4`), so the harness writes the segment base rate and skill score at the stamp. I leave both null.

**Reasoning quality 0.85.** This is the most careful analysis of the three:
- It states its anchor precisely (484 / 2,810 over OT2017–2024) and separates it from the terminal-band and relist tables.
- It weighs both sides of each vehicle issue with page cites to the petition and both oppositions: the waiver ruling on damages, the deleted covenant language as a contract-formation question, standing and preservation on the attainder question, and no developed split.
- It credits the response request as real interest while discounting the two-distribution count for the reason the record supports.
- It checks Newton against the source text instead of relying on the briefs.
- It is open about its limits: the reply was not provisioned, its figures are judgment rather than a fitted model, and its freshness claims cover the committed pack only.

It ends at the same well-calibrated 0.08 as claude-baseline.

**Leakage:** none. Forward mode, the log is 0.95 captured, and the external calls (Newton on CourtListener, two failed generic Rule 10 web attempts) were not about this petition and ran before resolution.
