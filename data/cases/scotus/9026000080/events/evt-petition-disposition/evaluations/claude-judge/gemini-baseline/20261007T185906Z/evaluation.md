# Evaluation: gemini-baseline — Scroggins v. City of Shreveport, No. 26-80 (cert, petition disposition)

## Outcome and scores

The event is a **cert**-stage petition disposition. `outcome.json` records `denied` on 2026-10-05 (first order list of OT2026, after the September 28, 2026 long conference), `actual_granted` = 0, one distribution, no CVSG, no noted dissent from denial.

- `correct` = 1: `predicted_disposition` `denied` matches `actual_disposition` `denied` exactly.
- `brier_score` = (0.001 − 0)² = 0.000001.
- `segment_base_rate` = 0.0502, `base_rate_basis` = `risk_set`. The prediction's frozen context carries both `band: baseline` and `salience_version: sal-v4`, matching the statpack's "Segment base rate by salience band (sal-v4)" heading. Pooling the bracketed `reached` figure resolved-weighted over every rendered Term strictly before Term 2026 (OT2017–OT2025) gives 638 / 12,720 = 0.05016, from the per-Term `prefix_est_grant_rate` × `prefix_weighted_resolved` fields in `metrics/statpack.json`. The caption says "Most recent 10 of 10 Term(s)", so the rendered window is the pack's whole window; no lookback divergence to flag.
- `brier_skill_score` = 1 − 0.000001 / (0.0502)² = 0.9996. The best Brier and skill on the cell, because it put the smallest number on an outcome that did not happen.
- `vote_accuracy` omitted (cert stage; never scored). `judgment_correct` null. No `semantic_grades` on a cert event. `claim_scores` left to the harness.

## Reasoning quality: 0.58

The call was right and the reasons given are the right reasons in outline, but the document is thin and the number is more extreme than the analysis behind it supports.

What it got right:

- The decisive features are all named: pro se paid petition, fact-bound error-correction questions on the summary-judgment standard and McDonnell Douglas, no split, no novel federal question, respondent's waiver, one distribution with no relist. It anchored on the correct band (`baseline`, sal-v4) and correctly restricted the pool to Terms strictly before 2026.
- It identified the published Fifth Circuit dissent as the only countervailing signal and sized it as more relevant to a possible dissent from denial than to the grant itself, which matched what happened (denied, no noted dissent).

What kept the score down:

- **The anchor is approximate.** "Approximately 4% to 6%" is the right range but is not a pooled figure; the prompt asks the predictor to pool the bracketed `reached` rate over the prior Terms, and the two peers did so to within a tenth of a point. A range is not an anchor the adjustments can be traced from.
- **The 0.1% number is not earned by the analysis.** A probability one-fiftieth of the band rate on a published-dissent petition is a strong claim. claude-baseline reached 0.5% only after reading the opinion below and finding that the majority rested on forfeiture and had flagged apparent fabricated citations, which this candidate never learned: it made no retrieval at all and did not engage the forfeiture question beyond listing it. Without those vehicle facts, the document's own reasons (pro se, fact-bound, waiver, no split) support something nearer the 0.5–1.5% of its peers than 0.1%. It happened to be right, but `reasoning_quality` grades soundness, and the sharpness here is asserted rather than argued.
- **The waiver inference is over-read.** "Indicating a lack of concern about a potential grant" treats a routine waiver as a signal about the respondent's assessment; the sounder use of a waiver is the one claude-baseline made, that the absence of a call for a response leaves no visible path to a grant from the current posture.
- **Brevity at the cost of substance.** The rationale is five sentences on the headline number and nothing on the limits of what it read. It did not mention the opinion below, the forfeiture ground's status as an adequate independent ground, or the pro se liberal-construction question's lack of traction at the appellate-forfeiture stage. Nothing in it is wrong; it is simply underdeveloped.

## Leakage: none; forward cell

`retrieval_log.json` records `mode: forward`, `result_capture_coverage` 0.0, 26 calls. Every call is marked `unobserved`, which is this engine's standing telemetry shape and not a defect, so each call is graded on its query. The queries are exclusively: reads of `AGENTS.md`, the predict prompt, `event.yaml`, `context.json`, `documents.json`, `questions-presented.txt`, `petition.txt`, and the 2026-10-04 snapshot; greps of `metrics/statpack.md` for the salience-band and relist tables; schema reads; the output writes; and `validate data`. There is no web, MCP, or corpus call, nothing names this case's Supreme Court docket or an order list, and nothing touches `data/qp-topics/`. The prediction was created 2026-10-04T20:18Z against the 2026-10-04 snapshot; the denial was entered 2026-10-05. The candidate's `retrieval.md` ("No retrieval beyond the provisioned inputs.") is consistent with the log. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My independent read is 0.03, formed before looking at the predictor's score: one pro se plaintiff, one city fire department, fact-bound Title VII claims resolved below on forfeiture, no split, no amicus, denied without a noted dissent.
