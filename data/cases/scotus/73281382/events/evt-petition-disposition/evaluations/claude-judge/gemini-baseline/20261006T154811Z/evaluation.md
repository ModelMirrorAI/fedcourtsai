# Evaluation of gemini-baseline — scotus/73281382, evt-petition-disposition

**Cell type.** Cert stage (`event.yaml` stage `cert`), forward mode. Outcome: petition **denied** on 2026-10-05 at the order list following the 2026-09-28 long conference, `actual_granted` 0, no noted dissent from denial, final distribution count 2 (no relist past what the prediction saw).

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| `brier_score` | 0.0225 | (0.15 − 0)² |
| `segment_base_rate` | 0.1724 | elevated band, `risk_set` basis (below) |
| `brier_skill_score` | 0.2428 | 1 − 0.0225 / (0.1724 − 0)² |
| `reasoning_quality` | 0.55 | see below |
| `leakage_suspected` | false | forward cell, log clean (below) |

**Base rate.** The prediction's frozen context carries `band` `elevated` **and** `salience_version` `sal-v4`, and the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" names the same version, so the basis is `risk_set`: the bracketed `reached` figure for `elevated`, pooled resolved-weighted over the rendered Terms strictly before the case's Term (2025). The caption says 10 of 10 Terms are rendered, so the rendered window is the pack's window and there is no window divergence to flag. Prior rows: 2024 17.9% (n=336), 2023 17.5% (354), 2022 19.0% (300), 2021 20.5% (342), 2020 16.1% (397), 2019 13.8% (334), 2018 15.9% (347), 2017 17.5% (400). Pooled: 484.4 / 2810 = **0.1724**. The naive baseline's Brier against this denial is 0.0297.

## What the prediction got right and wrong

Right outcome, and for the right headline reason: it named the BIO's preservation objection (the "officer purpose" theory was not the argument made below) as the vehicle problem most likely to sink the petition, and it correctly read the two distributions as one pre-call-for-response distribution plus one for the long conference rather than as two completed conferences. It also correctly identified the response request over the State's waiver as the one genuine positive signal and priced the CVSG prospect as negligible in a state criminal suppression case.

Its anchor is slightly loose: it quotes "~18%" for the elevated band "pooled over recent Terms" where the leakage-safe pool over the rendered prior Terms is 17.2%. The direction and size of its adjustment (down to 0.15) are defensible, and the outcome bore it out.

## What drove `reasoning_quality` (0.55)

The rationale is sound but thin. It engages one of the three arguments the BIO actually makes (preservation) and skips the other two that mattered as much to a denial: the absence of a genuine split (the petition pleads "confusion" rather than a conflict) and the Court's run of recent denials in exactly this knock-and-talk space, which the petition itself lists. It does not discuss what it read (the snapshot, the QP, and a `grep` of the BIO for "vehicle" and "preserve" are what the log shows) or where its judgment is most fragile, so a reader cannot tell how much of the BIO it weighed. The base-rate citation is approximate rather than pooled from the table it says it read. The pieces that are there are correct and well-chosen; there are just few of them, and the document reads as a summary of a conclusion rather than an analysis that could have come out the other way.

## Leakage

Forward cell. The prediction ran on 2026-09-16 against the 2026-09-15 snapshot, whose last entry is the 2026-07-01 distribution for the 2026-09-28 conference, so the petition was genuinely undecided at prediction time and provisioning did not mis-route a decided case forward. The retrieval log has 24 calls at `result_capture_coverage` 0.0, every row `unobserved`, so each is graded on its query: file reads of the prompt, `AGENTS.md`, the event, context, snapshot, provisioned documents, and `metrics/statpack.md`; a few `grep` calls over the BIO and snapshot; writes of its own outputs; and a `validate` run. No web, MCP, or corpus call, no `retrieved_doc_date` anywhere, no query naming this case's disposition, nothing under `data/qp-topics/`. The prose cites nothing postdating the snapshot. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Big case

My own read is 0.4 (recorded in `big_case`): a recurring Fourth Amendment question with real reach over everyday police practice, a response called for over a waiver, and amici from both the public-defense and gun-rights sides, but a single state suppression case with a contested preservation problem, no clean split, and a denial with no noted writing. I had seen the predictors' `big_case_score` values in the staged `prediction.json` before forming this read, so the read is not perfectly independent; I note that rather than pretend otherwise.

## Not scored here

The `claims` block and `predicted_reasoning.md` are the harness's and were read only for context. No `vote_accuracy` (cert stage; the prediction carries no votes anyway). No semantic set is declared on a cert cell, so no `semantic_grades` block. No `record/opinion/` slot was staged, as expected for a denial.
