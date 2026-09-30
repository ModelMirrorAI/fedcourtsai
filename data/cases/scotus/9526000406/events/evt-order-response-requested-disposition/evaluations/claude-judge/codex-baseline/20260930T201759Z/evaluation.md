# Evaluation: codex-baseline — DHS v. D.V.D., No. 26A406 (interim, response-requested disposition)

## Stage and what is mine to write

This is an **interim** cell (`event.yaml` stage `interim`). `correct` and `brier_score` are written per their definitions on the disposition axis; the harness re-stamps them. `segment_base_rate`, `brier_skill_score`, and `claim_scores` are the harness's, pooled by `stamp-cell` from the committed statpack over application-Terms strictly before 2026. On the committed pack that pool is Terms 2024 and 2025, 31 of 296 resolved substantive applications (about 10.5%), above the floor of 50, so a non-null stamp is expected; a null would point at the pack, not the pool. `base_rate_basis` is null structurally (no band on an application). No `vote_accuracy` and no `semantic_grades` on this stage.

## Outcome

Granted on 2026-09-29: stay of the February 25, 2026 order and judgment, application treated as a cert petition and granted (No. 26-426), argument set for December 2026, three Justices noting they would deny. Referral and two amicus briefs appear on the docket. `actual_disposition` granted, `actual_granted` 1.

## Scores

| field | value |
| --- | --- |
| predicted_disposition | granted |
| probability | 0.84 |
| correct | 1 |
| brier_score | 0.0256 |
| reasoning_quality | 0.85 |

## What the prediction got right and wrong

The call was right and the process was disciplined. The candidate computed the correct interim baseline (31/296), excluded the case's own Term and the pack-level rate, stated the pack's coverage caveat and the escalation-selection caveat, and recorded the statpack's commit vintage rather than asserting freshness. It grounded the upward adjustment mainly in the 2025 stays in this same litigation, and it did the one independent legal check that mattered most to the government's remedial argument: reading Garland v. Aleman Gonzalez footnote 2 in the opinion text to confirm that the declaratory-relief question was reserved rather than decided, and distinguishing dissent from holding. It kept applicant assertions (operational disruption, diplomatic harm) labeled as assertions, and it named the missing opposition as its main reason for discount.

The forecast document's timing window (September 29 to October 9) contained the actual disposition date, and it correctly anticipated a short order with a separate dissent rather than a majority explanation. It named a partial-relief order as the strongest alternative, which is the right failure mode for the denial-first resolver.

Where it was thinner than claude-baseline: it did not engage the §1231(h) textual point or the review-channeling argument beyond listing them, and it did not analyze the change in posture (final judgment versus preliminary injunction) beyond saying the differences "are not erased." The 0.16 residual is defended mostly by the absence of the response rather than by any specific way the Court might rule otherwise. Its web searches returned nothing, which it disclosed.

## Reasoning quality: 0.85

Correct baseline with vintage stated, a verified precedent check, careful separation of assertion from fact, and a well-calibrated number. Slightly below claude-baseline because the merits engagement is shallower and the residual is less specifically motivated.

## Leakage

Mode `forward`. Prediction created 2026-09-27; disposition 2026-09-29. The three web-search rows are `unobserved` and so graded on their queries, all of which name the 2022 Aleman Gonzalez opinion and none this application; the CourtListener calls fetched that opinion. No query reached this docket or its outcome, and the prose states the disposition is unknown. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false. The candidate's own `flags.json` is not staged; this rests on the log and prose.

## Big case

My read is 0.85 (see `big_case.notes`). Caveat: the predictor's score sits in `prediction.json`, which I read before forming my own, so the read is not strictly pre-exposure.
