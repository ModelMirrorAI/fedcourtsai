# Evaluation — codex-baseline
## Cell

Cert stage (`event.yaml` `stage: cert`, moment `distribution`). Outcome: petition **granted**, plenary route, resolved 2026-10-13 after two distributions (9/28/2026 long conference, relisted for 10/9/2026). `actual_granted` = 1. All three candidates are forward predictions made 2026-10-03 on a one-distribution snapshot, each with a frozen `context.band` of `federal` (sal-v4), so the segment base rate, its basis and the Brier skill score are the harness's risk-set stamp; I leave them null and refer only to "the stamped segment base rate". `correct` and `brier_score` are my elicited values for the stamp to compare. No votes scored (cert stage); no semantic set declared (cert stage), so no `semantic_grades`. Claims are scored in code, not here.

## Score

P(grant) 0.78, predicted `granted` → `correct` 1, Brier (0.78−1)² = 0.0484.

## Reasoning quality: 0.80

Sound and disciplined. It anchored on the correct surface — the sal-v4 `federal` reached figures pooled over Terms strictly before the case's own (2017–2024, n≈181, ≈73%) — and explicitly declined the terminal relist/CVSG tables as forward hazards. Its upward adjustment rests on concrete features of the Fourth Circuit opinion it actually read: a published, divided decision announcing a narrowing construction of the material-support bar against the agency, with a dissent pointing to other circuits' food-and-shelter cases. It priced SG participation as already in the anchor rather than double-counting it, and was candid that it had not verified a square split and lacked the petition/BIO text. It also put 0.65 on an additional distribution, which is what happened. Modest deductions: the upward step is lightly quantified, and it did not engage with vehicle issues (respondent's removal, alternative grounds on remand) that a full analysis would weigh.

## Leakage

Forward; `not_applicable`. See `leakage.notes`: only the pre-petition lower-court opinion was retrieved; nothing post-resolution.
