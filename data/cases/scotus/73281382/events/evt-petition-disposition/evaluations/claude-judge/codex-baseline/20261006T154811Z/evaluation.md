# Evaluation of codex-baseline — scotus/73281382, evt-petition-disposition

**Cell type.** Cert stage (`event.yaml` stage `cert`), forward mode. Outcome: petition **denied** on 2026-10-05 at the order list following the 2026-09-28 long conference, `actual_granted` 0, no noted dissent from denial, final distribution count 2 (no relist past what the prediction saw).

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| `brier_score` | 0.0144 | (0.12 − 0)² |
| `segment_base_rate` | 0.1724 | elevated band, `risk_set` basis (below) |
| `brier_skill_score` | 0.5154 | 1 − 0.0144 / (0.1724 − 0)² |
| `reasoning_quality` | 0.80 | see below |
| `leakage_suspected` | false | forward cell, log clean (below) |

**Base rate.** The prediction's frozen context carries `band` `elevated` **and** `salience_version` `sal-v4`, and the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" names the same version, so the basis is `risk_set`: the bracketed `reached` figure for `elevated`, pooled resolved-weighted over the rendered Terms strictly before the case's Term (2025). The caption says 10 of 10 Terms are rendered, so the rendered window is the pack's window and there is no window divergence to flag. Prior rows: 2024 17.9% (n=336), 2023 17.5% (354), 2022 19.0% (300), 2021 20.5% (342), 2020 16.1% (397), 2019 13.8% (334), 2018 15.9% (347), 2017 17.5% (400). Pooled: 484.4 / 2810 = **0.1724**. The candidate pooled the same rows to 17.24% on n=2,810, which matches. The naive baseline's Brier against this denial is 0.0297.

## What the prediction got right and wrong

Right outcome at the lowest probability of the three candidates, hence the best Brier and skill on this cell. The anchor is exactly the leakage-safe pool, taken from the right table under the right version, with the window stated. It correctly declined to stack a relist premium on top of the band because the second distribution followed a call for response that intervened before the first scheduled conference, which is the right reading of this docket. It treated the response request and the amicus support as attention signals that "do not establish four votes," which is how the Court in fact treated them.

Its three substantive adjustments all pointed the right way and were each argued from the briefs with page cites: preservation is contested rather than settled (fairer to the petitioner than the BIO's framing, and it still counted the friction against the petition); the asserted division is confusion rather than a clean conflict; and the question as written overstates the rule the facts require, leaving error correction as the competing characterization. It also correctly distinguished the caption's state respondent from the `state` petitioner band.

## What drove `reasoning_quality` (0.80)

Careful information-boundary discipline (what was and was not read, that the reply's text was not provisioned, that failed web retrievals were not treated as verification), a correctly pooled anchor, and three independent, well-sourced downward adjustments with the upward signals weighed honestly against them. The adjustment from 17.2% to 12% is stated as judgmental rather than fitted, which is the right epistemic posture. What keeps it short of the top: it does not use the petition's own list of recent knock-and-talk denials (Bovat, Chute, Frederick, Christensen, Morgan, Brienza), which is the single strongest piece of track-record evidence available in the provisioned documents; and the section on the terminal relist and CVSG slices, while correctly labeled as descriptive, adds length without changing the number. A stray reference to not having "watched the video" is harmless but suggests the document was not tightened. The quoted snapshot creation date (September 4) is not something I can verify from my own, later snapshot; nothing turns on it.

## Leakage

Forward cell. The prediction ran on 2026-09-16 against the 2026-09-15 snapshot, whose last entry is the 2026-07-01 distribution for the 2026-09-28 conference, so the petition was genuinely undecided at prediction time and provisioning did not mis-route a decided case forward. The retrieval log has 27 calls at `result_capture_coverage` 0.89. The three `web-search` rows are `unobserved` and so graded on their queries: a Jardines query and two document opens (the Bovat v. Vermont statement PDF and Cornell's Jardines page), all general precedent rather than this docket. The one captured CourtListener `search` row is for "Bovat v. Vermont" and, per the candidate's `retrieval.md`, returned 0. Every other call is a shell read of the prompt, schemas, provisioned snapshot and documents, and the statpack, or a write of its own outputs. No `retrieved_doc_date` anywhere, no query naming this case's disposition, nothing under `data/qp-topics/`. The candidate's prose states it neither sought nor encountered the outcome, and the log agrees. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Big case

My own read is 0.4 (recorded in `big_case`): a recurring Fourth Amendment question with real reach over everyday police practice, a response called for over a waiver, and amici from both the public-defense and gun-rights sides, but a single state suppression case with a contested preservation problem, no clean split, and a denial with no noted writing. I had seen the predictors' `big_case_score` values in the staged `prediction.json` before forming this read, so the read is not perfectly independent; I note that rather than pretend otherwise.

## Not scored here

The `claims` block and `predicted_reasoning.md` are the harness's and were read only for context. No `vote_accuracy` (cert stage; the prediction carries no votes anyway). No semantic set is declared on a cert cell, so no `semantic_grades` block. No `record/opinion/` slot was staged, as expected for a denial.
