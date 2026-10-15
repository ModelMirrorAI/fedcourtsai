# Evaluation — codex-baseline

## Cell

- **Stage: interim.** Stay application 26A477, which asked the Court to stay a Fourth Circuit mandamus order that set a deadline for the FCC to decide. Outcome (`outcome.json`): `denied`, `actual_granted` 0, resolved 2026-10-14. The committed record shows the Court denied the application **as moot** in a per curiam; Justices Sotomayor and Jackson would have denied it outright.
- `correct` and `brier_score` below are my independent reading. The harness recomputes both at the stamp. **The interim baseline and skill are the harness's** (`stamp-cell` pools the substantive slice over prior application-Terms). I wrote neither, and I left `base_rate_basis` null. The prediction froze no band (`band: null`), which is the normal interim shape, so no flag.
- `vote_accuracy` is omitted because this is not a merits cell. There is no `semantic_grades` block because no semantic set is declared on an interim cell. `claim_scores` belong to the harness.
- **Leakage: forward.** The prediction ran under an arrival-position cut (anchor index 0, cutoff 2026-10-09). It was written on 2026-10-14, the day the order issued. Its log shows no retrieval of the disposition, so it is graded `not_applicable`. See the cell-level `flags.json` note on same-day minting.

## Scores

P(grant) 0.84, predicted `granted`. Actual `denied` (as moot). correct = 0, Brier = 0.7056.

## Reasoning quality: 0.55

This is the most careful reading of the record. The candidate states the resolver boundary: mixed relief and withdrawals count as ungranted. It reads the 9.65% pool with its coverage caveats, noting that 2016–2022 are unparsed rather than denials, and treats the pool as an unconditional starting point.

It grounds the upward move in the earlier 26A274 stay. Unlike gemini-baseline, it engages the contrary reasoning in the appendix. It cites the panel majority's point about five months of unresolved review and an already-circulated proposed order. It cites the concurrence's distinction between ordering a decision and ordering a result. It explicitly declines the applicants' categorical jurisdictional inference.

The weakness is calibration rather than analysis. The facts it surfaced (a proposed order already circulating, a noon Oct 9 deadline, an agency able to act) point straight at the moot-out that resolved the event. Yet the candidate folded that into an unspecified "procedural developments" residual and stayed at 0.84. claude-baseline named mootness directly; this one only came close. The reasoning is strong but not reflected in the number. Its retrieval (Hollingsworth via CourtListener) was appropriate and disclosed.

## Leakage

Forward. The unobserved web searches and the U.S. Code fetch targeted the general stay standard and the statute. The CourtListener calls retrieved Hollingsworth v. Perry (2010). No query concerned this application's disposition. Graded `not_applicable`.
