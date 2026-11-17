# Evaluation — codex-baseline, Jabateh v. United States (No. 26-440), cert stage

**Outcome:** petition denied on 2026-11-16 after one distribution, with no response call, no CVSG and no noted dissent.

**Prediction:** `denied`, P(grant) = 0.035. `correct` = 1; `brier_score` = 0.001225. The segment base rate and skill score are the harness's to stamp. No votes are scored on a cert cell, and no semantic set is declared, so there is no `semantic_grades` block.

## Reasoning (`reasoning_quality` = 0.82)

A careful rationale with the best legal engagement of the three. It reads the appendix against the petition and identifies the precise obstacle: the panel separated the relitigation bar from procedural default, so the government's alleged waiver of default does not answer the bar, and it declined to treat a construction announced in the petitioner's own appeal as an intervening change. The document then checks *Davis* itself and notes that its holding concerns a change in law after the earlier appeal, which is why summary reversal is harder than the petition suggests. It also avoids equating exclusion from § 1546(a) with factual innocence. The anchor is stated clearly, with the pooled count checked against the statpack JSON.

Weaknesses: the adjustment from 5.1% to 3.5% is the smallest of the three and the least explained. The waiver is called "only modest evidence", which understates how rarely a waived petition with no response call is granted; the document gives no path arithmetic (response call times conditional grant) to support 3.5%, and its own 12% redistribution figure would imply a conditional grant rate near 30%. The result is the highest Brier of the three, though still small. A good deal of space goes to caveats about corpus vintage that do not bear on the forecast.

## Predicted reasoning (`predicted_reasoning_quality` = 0.75)

Central claims: an ordinary unexplained denial; zero further distributions; no CVSG; no separate writing. All four held. The grant-conditional forecast is the most committed of the three (summary reversal with remand at 65%, expressly not a GVR), but the condition never occurred and it earns nothing either way.

The resolved content is specific about the path and correct, at about the same level as a competent default reading of a waived, splitless petition. "At or soon after that conference" is slightly looser on timing than it could have been.

## Leakage

Forward cell: prediction run 2026-10-30 on the 2026-10-30 snapshot, before the 2026-11-16 denial. Log is 98% captured. Calls are shell reads of the provisioned record and statpack, one fedcourts query for summary reversals with --decided-before 2026-10-30, CourtListener searches for Davis v. United States, 417 U.S. 333 (1974), and one web search on Bousley whose result is unobserved; graded on its query, it names general precedent, not this case. Subagent messages are confined to the appendix and statpack. Nothing queries this petition's docket or caption, and the prose states the outcome was not sought. No read under data/qp-topics/. Graded `not_applicable`; `leakage_suspected` = false.

## Big case

My read is 0.12: one prisoner's collateral-review petition from a non-precedential ruling with no split, denied without comment.
