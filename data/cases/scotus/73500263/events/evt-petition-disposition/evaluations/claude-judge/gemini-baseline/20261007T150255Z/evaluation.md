# Evaluation: gemini-baseline — scotus/73500263, evt-petition-disposition

**Stage:** cert (event.yaml `stage: cert`, moment `distribution`). **Mode:** forward.
**Outcome:** `denied` on 2026-10-05, `actual_granted` 0, one distribution, no CVSG, no noted dissent; the order recorded that Justice Alito took no part.

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` denied == `actual_disposition` denied |
| `brier_score` | 0.000025 | (0.005 − 0)² |
| `segment_base_rate` | 0.051209 | baseline band, sal-v4, bracketed `reached` pooled over Terms 2017–2024 |
| `base_rate_basis` | `risk_set` | prediction froze `band: baseline` with `salience_version: sal-v4`; the table heading is sal-v4 |
| `brier_skill_score` | 0.990467 | 1 − 0.000025 / 0.051209² |
| `reasoning_quality` | 0.58 | below |

Base rate: the prediction's frozen context carries both a band and a salience version, and the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" names the same version, so the risk-set figure applies. I pooled the bracketed `reached` figures resolved-weighted over every rendered Term strictly before Term 2025, which is 2017–2024 (the caption says 10 of 10 Terms are rendered, so no lookback divergence arises). From the unrounded `statpack.json` rows that is 593 / 11,580 = 0.051209. `vote_accuracy` is omitted (cert stage). No `semantic_grades` block: no semantic set is declared on a cert event.

## What the prediction got right and wrong

The call was right and the number was the lowest of the three, so this candidate takes the best Brier and skill on the cell. The reasoning, though, is thin, and the skill number should not be read as a measure of it: on a denied petition a lower probability wins mechanically, and the question for `reasoning_quality` is whether the analysis earned it.

What it got right, and from the record: the respondent's waiver on June 11, the single distribution for September 28, the petitioner being an individual, and the correct inference that the Court almost never grants a waived-response petition without first calling for a response, which would itself show up as a further distribution. The characterisation of the dispute as a fact-bound private ERISA QDRO matter is accurate. These are the signals that decided the cell.

What it did not do. The anchor is quoted as "5.7% (Term 2024)," a single Term's bracketed figure rather than the pooled prior-Term rate the contract asks for (5.1% over 2017–2024); the direction and magnitude happen to be close, but it is the wrong pooling and the write-up does not say why one Term was chosen. It did not read the opinion below, so it never engaged with the two vehicle facts the other candidates found and that make this petition weaker than its docket profile alone: that the panel decided a state-law contract question and never addressed a Chenery rationale, and that the statutory theory behind QP 2 was declined below as raised for the first time on appeal. It did not notice that the petitioner is pro se, only that he is "an individual," though the snapshot and the petition's signature block both show it, and it did not notice the sealing-motion order's Alito nonparticipation. The rationale is four short paragraphs and does not walk through the five declared claims at all. None of this was needed to get the disposition right, which is why the score is in the middle rather than low, but a 0.005 call with this much of the record unread is a well-aimed guess more than an analysis.

## Leakage

Forward cell, graded `not_applicable`, `retrieved_outcome_material: false`, `leakage_suspected: false`. Every call in the log carries `result_capture: unobserved` (coverage 0.0), which is the engine's standing shape rather than a defect, so each call is graded on its query. All are local reads of the predict prompt, AGENTS.md, this case's provisioned record (event, context, documents manifest, QP text, the 2026-09-16 snapshot), the committed statpack, and the prediction schema, followed by the output writes and `validate` runs. There is no MCP, corpus-query, or web call and nothing names `data/qp-topics/`. The candidate's retrieval note says "No retrieval beyond the provisioned inputs," which matches the log. Nothing in the information set could have carried the October 5 outcome.

## Big case

My own read, formed from the record before weighing the candidate's: 0.05. A single participant's pension calculation turning on the word "may" in one domestic-relations order, decided below on state contract law, denied with no call for a response and no separate writing. The candidate's 0.05 is in the same place.
