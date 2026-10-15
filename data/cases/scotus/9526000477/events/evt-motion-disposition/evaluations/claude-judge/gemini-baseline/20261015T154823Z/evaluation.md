# Evaluation — gemini-baseline

## Cell

- **Stage: interim.** Stay application 26A477, which asked the Court to stay a Fourth Circuit mandamus order that set a deadline for the FCC to decide. Outcome (`outcome.json`): `denied`, `actual_granted` 0, resolved 2026-10-14. The committed record shows the Court denied the application **as moot** in a per curiam; Justices Sotomayor and Jackson would have denied it outright.
- `correct` and `brier_score` below are my independent reading. The harness recomputes both at the stamp. **The interim baseline and skill are the harness's** (`stamp-cell` pools the substantive slice over prior application-Terms). I wrote neither, and I left `base_rate_basis` null. The prediction froze no band (`band: null`), which is the normal interim shape, so no flag.
- `vote_accuracy` is omitted because this is not a merits cell. There is no `semantic_grades` block because no semantic set is declared on an interim cell. `claim_scores` belong to the harness.
- **Leakage: forward.** The prediction ran under an arrival-position cut (anchor index 0, cutoff 2026-10-09). It was written on 2026-10-14, the day the order issued. Its log shows no retrieval of the disposition, so it is graded `not_applicable`. See the cell-level `flags.json` note on same-day minting.

## Scores

P(grant) 0.88, predicted `granted`. Actual `denied` (as moot). correct = 0, Brier = 0.7744.

## Reasoning quality: 0.35

The candidate correctly identifies the 9.65% pooled interim baseline. It correctly identifies the main reason to move far above it: the Court stayed the earlier iteration of this dispute a month before, and the new mandamus order arguably works around that stay's premise.

The analysis is one-sided. It names no contrary argument from the record. It does not engage the panel's rationale that an order to *decide* differs from an order dictating a result. It does not note that the agency could act before the deadline and moot the application. The only uncertainty it discusses is a possible administrative stay, which it treats as a step toward a grant.

The event resolved through exactly the path the candidate never considered: the application became moot. At 0.88, the candidate was the most confident of the three. Its rationale is also the thinnest, and the confidence is not earned by the analysis on the page.

## Leakage

Forward. No call result was captured (coverage 0.0), so the cell is graded on its queries. Its two CourtListener searches targeted the prior proceeding (26A274 / "NRCC v. Brown"), not this application. No outcome material was sought. Graded `not_applicable`.
