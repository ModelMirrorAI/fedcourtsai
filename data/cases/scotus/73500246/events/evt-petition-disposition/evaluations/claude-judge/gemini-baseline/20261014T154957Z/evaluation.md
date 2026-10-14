# Evaluation — gemini-baseline
## Cell

Cert stage (`event.yaml` `stage: cert`, moment `distribution`). Outcome: petition **granted**, plenary route, resolved 2026-10-13 after two distributions (9/28/2026 long conference, relisted for 10/9/2026). `actual_granted` = 1. All three candidates are forward predictions made 2026-10-03 on a one-distribution snapshot, each with a frozen `context.band` of `federal` (sal-v4), so the segment base rate, its basis and the Brier skill score are the harness's risk-set stamp; I leave them null and refer only to "the stamped segment base rate". `correct` and `brier_score` are my elicited values for the stamp to compare. No votes scored (cert stage); no semantic set declared (cert stage), so no `semantic_grades`. Claims are scored in code, not here.

## Score

P(grant) 0.85, predicted `granted` → `correct` 1, Brier (0.85−1)² = 0.0225.

## Reasoning quality: 0.50

Right direction, thin support. The core points — SG petitioner, published decision rejecting a BIA precedent (`Matter of A-C-M-`), CVSG impossible — are correct and relevant. But the document asserts a "clean circuit split" on the strength of a single web search, without reading the opinion or identifying the conflicting circuits; it quotes the case's **own** Term row (2025) as "the most recent term" base rate rather than pooling strictly prior Terms, and gives no explicit anchor figure; and it concludes the likelihood of a grant is "extremely high" while dismissing vehicle risk in one sentence. Its specific route expectation (grant at the first conference without relist) did not occur — the petition was relisted once — though that sits in the forecast document, which is not graded here. The number was well calibrated in outcome; the analysis behind it is under-evidenced and overconfident in tone.

## Leakage

Forward; `not_applicable`. Retrieval log coverage 0.0 (all rows unobserved — the engine's standing shape), graded on queries: one web search about the lower-court case. Nothing outcome-revealing could exist at prediction time.
