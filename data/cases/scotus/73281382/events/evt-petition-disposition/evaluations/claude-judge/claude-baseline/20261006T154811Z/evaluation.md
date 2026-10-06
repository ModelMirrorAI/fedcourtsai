# Evaluation of claude-baseline — scotus/73281382, evt-petition-disposition

**Cell type.** Cert stage (`event.yaml` stage `cert`), forward mode. Outcome: petition **denied** on 2026-10-05 at the order list following the 2026-09-28 long conference, `actual_granted` 0, no noted dissent from denial, final distribution count 2 (no relist past what the prediction saw).

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| `brier_score` | 0.0169 | (0.13 − 0)² |
| `segment_base_rate` | 0.1724 | elevated band, `risk_set` basis (below) |
| `brier_skill_score` | 0.4313 | 1 − 0.0169 / (0.1724 − 0)² |
| `reasoning_quality` | 0.85 | see below |
| `leakage_suspected` | false | forward cell, log clean (below) |

**Base rate.** The prediction's frozen context carries `band` `elevated` **and** `salience_version` `sal-v4`, and the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" names the same version, so the basis is `risk_set`: the bracketed `reached` figure for `elevated`, pooled resolved-weighted over the rendered Terms strictly before the case's Term (2025). The caption says 10 of 10 Terms are rendered, so the rendered window is the pack's window and there is no window divergence to flag. Prior rows: 2024 17.9% (n=336), 2023 17.5% (354), 2022 19.0% (300), 2021 20.5% (342), 2020 16.1% (397), 2019 13.8% (334), 2018 15.9% (347), 2017 17.5% (400). Pooled: 484.4 / 2810 = **0.1724**. The candidate pooled the same rows to about 17.2% on n=2,810, which matches. The naive baseline's Brier against this denial is 0.0297.

## What the prediction got right and wrong

Right outcome at 0.13, between the other two candidates on Brier and skill. The anchor is the correct leakage-safe pool from the right table and version. Its reading of the docket is the sharpest of the three: the two distributions are not two conferences, since the call for response on April 27 pre-empted the May 1 conference, so the long conference was the first real look at a fully briefed petition; the response request is the one signal not already priced into the band (the band lattice is relist count, CVSG, originating circuit, and petitioner class, which `docs/salience.md` confirms); and the band's population already contains call-for-response redistributions, so no relist premium is warranted.

Its downward adjustments cover the whole case for denial, each tied to the provisioned briefs: preservation (with the BIO's record cites to the suppression transcript and both state appellate briefs), the "confusion"-not-conflict framing of the split, the petition's own list of six knock-and-talk denials since 2018, the contested factual premise and alternative exigency ground, and the unreasoned state supreme court affirmance. The upward factors (response request, the Bovat constituency, counsel and amici, a dissent below) are stated and weighed rather than waved at. The outcome vindicated the net.

## What drove `reasoning_quality` (0.85)

This is the most complete and best-organized rationale of the three: inputs enumerated, anchor pooled correctly, docket signals read with care, the merits adjustments exhaustive and sourced, and a genuine uncertainty section that says where the number would be wrong (if the call for response reflected more than one chambers' interest, 0.13 is too low; if it was prompted by a Justice drafting a statement, the grant number is fine but the writing numbers are low). It discloses that its corpus query and CourtListener searches did not inform the number. Two things keep it from higher: the assertion that the call-for-response-over-waiver population "grants at something like the low-to-mid teens" is offered from "experience" with no source, and that unsourced figure does real work in the argument; and the rationale is some way longer than its content requires. Neither is a soundness error.

## Leakage

Forward cell. The prediction ran on 2026-09-16 against the 2026-09-15 snapshot, whose last entry is the 2026-07-01 distribution for the 2026-09-28 conference, so the petition was genuinely undecided at prediction time and provisioning did not mis-route a decided case forward. The retrieval log has 26 calls at `result_capture_coverage` 1.0. One corpus query (`fedcourts query --court scotus --era 2020s --disposition granted`, generic recent grants, which the candidate's `retrieval.md` says returned no on-point priors) and two captured CourtListener `search` calls on knock-and-talk and Jardines terms. The only `retrieved_doc_date` in the log is 2026-06-29 on the second search, which the candidate identifies as Chatrie v. United States: a different case, decided before this prediction and well before this event's resolution, so legitimate forward context and not outcome material about this petition. The remaining calls read the prompt, the provisioned snapshot and documents, `docs/salience.md`, the schema, and the statpack, or write its own outputs. No query naming this case's disposition, nothing under `data/qp-topics/`. The prose states it did not know the outcome and that the conference postdated the run. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Big case

My own read is 0.4 (recorded in `big_case`): a recurring Fourth Amendment question with real reach over everyday police practice, a response called for over a waiver, and amici from both the public-defense and gun-rights sides, but a single state suppression case with a contested preservation problem, no clean split, and a denial with no noted writing. I had seen the predictors' `big_case_score` values in the staged `prediction.json` before forming this read, so the read is not perfectly independent; I note that rather than pretend otherwise.

## Not scored here

The `claims` block and `predicted_reasoning.md` are the harness's and were read only for context. No `vote_accuracy` (cert stage; the prediction carries no votes anyway). No semantic set is declared on a cert cell, so no `semantic_grades` block. No `record/opinion/` slot was staged, as expected for a denial.
