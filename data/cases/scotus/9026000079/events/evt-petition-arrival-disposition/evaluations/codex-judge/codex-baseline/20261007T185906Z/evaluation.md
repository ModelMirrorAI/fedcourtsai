# Evaluation: codex-baseline

## Outcome and numerical score

The supplied cert-stage outcome records denial on October 5, 2026, with `actual_granted = 0`. The forecast label `denied` is correct, so correctness is 1. The 0.05 grant-family probability gives Brier score `(0.05 - 0)^2 = 0.0025`. This single denial does not establish whether a more confident denial probability was better justified ex ante.

## Reasoning quality: 0.80

The rationale carefully distinguishes a frozen arrival risk set from a terminal low-salience population. It identifies strictly prior Terms, explains why a circuit aggregate mixing fee classes is only secondary, and candidly declines to infer the underlying legal question from the caption. Its express acknowledgment that the petition, questions presented, and lower-court opinion were unavailable is a strength. Remaining near the stated historical anchor is a coherent response to those limits rather than unsupported case-specific confidence.

The deduction is for limited substantive analysis and a modest but not independently quantified downward adjustment to 5%. An absence of grounds for increasing a prior is not, on its own, a strong reason to decrease it. The analysis supplies no actual vehicle assessment or competing legal interpretations, appropriately because the source material was missing. Its decision not to use the August 14 waiver is cautious, but forward mode permitted that pre-resolution signal; abstaining from it is not a required leakage safeguard and earns no separate integrity bonus. The correct denial does not cure those analytical limits.

## Baseline unavailable under the version rule

The prediction froze Term 2026, band `baseline`, and `sal-v3`. The committed `metrics/statpack.md` table instead names `sal-v4`. Its rates cannot be paired with this frozen band, even though the band names coincide. Both `segment_base_rate` and `brier_skill_score` are omitted, with `base_rate_basis = null`, and no terminal substitute is used. The historical pooled count in the rationale is not independently verified against this differently versioned table. The shared flags file records the mismatch rather than attributing it to a prediction error.

## Leakage and scoring scope

The log records forward mode and seven captured calls on August 16, 2026, before resolution. Capture coverage 1.0 describes those calls, not a guarantee of a complete, fully readable history: multiple shell query slices are truncated, and the reported pre-petition opinion search and HTTP 429 are not separately visible. The prose reports no outcome retrieval and does not presuppose the October 5 denial. The later waiver is openly acknowledged as information available before resolution. Nothing shown supports a mis-provisioned decided case, so retrieved outcome material is false, influence is `not_applicable`, and leakage suspicion is false. Redacted strings and null document dates are not treated as affirmative evidence either way.

Only `reasoning.md` is graded for analytical quality. The forecast document was read for context; its accuracy and the structured claim probabilities do not enter that score. Mechanical claim scores are left to the harness, and no cert vote score, semantic grade, or big-case assessment is supplied.
