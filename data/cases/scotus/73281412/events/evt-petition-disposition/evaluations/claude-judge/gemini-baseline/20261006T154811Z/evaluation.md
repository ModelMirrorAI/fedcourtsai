# Evaluation of gemini-baseline — scotus/73281412, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition in No. 25-1128, Alexander v. Philip R. Taft Psy D and Associates, was **denied on October 5, 2026** after the September 28 long conference, with no noted dissent from denial and no further relist (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 2).

- `correct` = 1: the candidate predicted `denied`.
- `brier_score` = (0.12 − 0)² = **0.0144**.
- `segment_base_rate` = **0.1722**, basis `risk_set`. The prediction froze `band: elevated` under `salience_version: sal-v4`, matching the statpack's sal-v4 band table heading. I pooled the bracketed `reached` figure for `elevated` over Terms 2017–2024 (weighted n = 2,810; 484.0 weighted grants), the full strictly-prior window the pack renders, which coincides with the in-code ten-Term lookback.
- `brier_skill_score` = 1 − 0.0144 / (0.1722)² = **0.515**.

No `vote_accuracy`, `judgment_correct`, or `semantic_grades` on a cert cell. `claim_scores` is the harness's.

## Reasoning quality: 0.45

The number landed in a reasonable place and the skill score is identical to codex-baseline's, but `reasoning_quality` grades the analysis, and the analysis is thin and contains errors.

What it got right:

- It identified the `elevated` band, the roughly 17% reached rate for prior Terms, and the key procedural fact that the second distribution followed a call for response rather than a conference, so the petition was effectively at its first fully briefed conference.
- It read the Fifth Circuit opinion itself via CourtListener and confirmed the 12(b)(6) posture.

What pulled the grade down:

- **Misread relist cut.** It takes "27.8% in the statpack for bucket 2" as the relist rate this petition would carry if the second distribution were a true relist. A `distribution_count` of 2 is one relist, which is the pack's bucket 1 (granted 8.2%, GVR 5.1%), not bucket 2. The adjustment therefore starts from the wrong row, and the final 12% is described as a split between 27.8% and 1.2% with no stated weighting.
- **GVR theory does not work.** The reasoning calls QP 3's reliance on NRA v. Vullo (2024) "a clean vehicle for a GVR if the Fifth Circuit misapplied it." A GVR responds to an intervening decision; Vullo was decided eighteen months before the Fifth Circuit's December 2025 judgment, and the panel was bound to apply it. Misapplication of existing precedent is an error-correction argument, not a GVR predicate. claude-baseline correctly noted that no intervening decision supports a GVR here.
- **The stated main uncertainty is misdirected.** It worries that the Fifth Circuit "rested on alternative independent grounds for qualified immunity." The briefs in opposition make clear the panel did not reach qualified immunity; the actual vehicle problems (the unchallenged deliberate-indifference dismissal of the Taft respondents, the alternative "potentially suicidal" holding, unresolved Monell liability) are the ones the other two candidates found. The log shows the candidate read only the first hundred lines of the 77-page opposition file plus a grep for a summary of argument, which is consistent with having missed them.
- **"The CFR strongly signals Court interest"** overstates a routine signal: a call for response after a waiver means at least one chambers wanted an answer, which both other candidates weighed more carefully, and the final denial without writing confirms the interest was modest.
- No engagement with the petition's own concessions (the admittedly false suicide report, the "not simple enough for summary reversal" line) or with the absence of a circuit split as framed.

The forecast document (`predicted_reasoning.md`) was read for context only and is not scored.

## Leakage

Mode `forward`; `influenced_prediction` = `not_applicable`; `retrieved_outcome_material` = false; `leakage_suspected` = false. The prediction was made September 17, 2026, eighteen days before the denial. The log's `result_capture_coverage` is 0.0, the engine's standing shape, so every call is graded on its query: a corpus query for the Fifth Circuit case 24-10663, a corpus query bounded to `--decided-before 2026-09-17`, a CourtListener opinion search for "Ronnie Alexander" AND Taft, and two `read_document` chunks of the lower-court opinion. All target the lower-court record; none seeks this petition's disposition. No `data/qp-topics/` read. The case was not mis-provisioned forward.

## Big case

My independent read is 0.28 (see `big_case.notes`). The candidate's own stakes score was visible in the staged `prediction.json` when I formed mine; my read rests on the record described in the notes.
