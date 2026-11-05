# Evaluation: codex-baseline

## Cell
Interim stage: *Akerman v. MSPB*, No. 26A612. The application was for an injunction pending certiorari, submitted to the Chief Justice on Oct 20, 2026, docketed Oct 30, and denied by the Chief Justice on Nov 3, 2026. `outcome.json`: `interim_reading` denied, `interim_granted` 0. There was no response request, no referral and no amicus. Scoring uses the finer interim reading: `correct` is 1 for a prediction on the ungranted side, and `brier_score` = p². The interim baseline (`segment_base_rate`) and `brier_skill_score` are the harness's to stamp from the statpack's pooled finer counts. I quote no rate of my own. The prediction carries no cert band (`context.band` null), so no band flag applies. Interim cells declare no semantic set, so this file has no `semantic_grades` block, and `vote_accuracy` is omitted (interim stage).

## Score
P(grant) = 0.03 and the prediction was **denied**, which is correct. Brier 0.0009.

## Reasoning quality: 0.75
The candidate read the record carefully and correctly: an injunction application submitted to the Chief Justice, no rungs climbed, and the application text empty at the time, which it honestly treated as unavailable. It retrieved and read Brown v. Gilmore (in chambers) for the All Writs injunction standard and limited its use to the procedural principle. It also flagged a real chronology wrinkle (submitted Oct 20, docketed Oct 30).

Its base-rate audit was conservative. It declined any anchor because the markdown table lacked the finer columns, but it did not check the JSON pack. That caution is defensible but slightly over-lawyered. The probability is well calibrated for the posture. The weakness is that much of the document is caveats rather than analysis. It declined a big-case score instead of forming a read from the caption and posture.

## Leakage
Forward cell. No query targeted this application's docket or outcome. The web searches were generic (unobserved, graded on query). The CourtListener read was a 2001 in-chambers opinion. Clean: `not_applicable`.

## Predicted reasoning: 0.85
Central claims: (1) denial by short unexplained order; (2) modal route: the Chief Justice rather than referral; (3) no response request and no amicus; (4) November 2026 timing. All were borne out (Nov 3 denial by the Chief Justice, no referral, no response). The route and timing claims were specific. Some of the content is hedged ("referral followed by denial remains an alternative"), which keeps it below the top anchor.

## Big case
My read is 0.03.
