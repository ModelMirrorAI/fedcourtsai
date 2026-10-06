# Evaluation of gemini-baseline — Gasper v. Wisconsin, No. 25-1191 (evt-petition-disposition)

## Cell and outcome

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition was **denied on 2026-10-05** after the September 28 long conference, with no noted dissent (`outcome.json`: `actual_disposition` `denied`, `actual_granted` 0, `noted_dissent_from_denial` false, two distributions under `dist-v2`). The docket: petition filed April 14, Wisconsin waived April 21, distributed May 5 for the May 21 conference, response requested May 8, BIO June 1, one amicus June 8, redistributed June 17 for September 28, denied October 5.

## Scores

| field | value | how |
| --- | --- | --- |
| `correct` | 1 | `denied` == `denied` |
| `brier_score` | 0.16 | (0.40 − 0)² |
| `segment_base_rate` | 0.1724 | elevated band, `sal-v4`, bracketed `reached` figures pooled resolved-weighted over Terms 2017–2024 (n = 2810) |
| `base_rate_basis` | `risk_set` | the prediction froze `band: elevated` with `salience_version: sal-v4`, and the statpack table heading is `sal-v4` |
| `brier_skill_score` | −4.385 | 1 − 0.16 / 0.1724² |
| `reasoning_quality` | 0.30 | below |

Base-rate detail. The prediction's frozen `context` carries both `band` (`elevated`) and `salience_version` (`sal-v4`), Term 2025, so the risk-set basis applies. The "Segment base rate by salience band (sal-v4)" table renders 10 of 10 Terms; the Terms strictly before 2025 that carry data are 2017–2024. Pooling the bracketed `reached` rate × `n` across those eight rows: 484.4 weighted grants over 2810 weighted resolved = 0.17238. The in-code ten-Term lookback is shortened by the pack's coverage to the same eight Terms, so there is no window divergence to flag. `vote_accuracy` is omitted (cert stage). No `semantic_grades` (cert event). `claim_scores` and `process_version` are the harness's.

## What the prediction got right and wrong

Right: the label, and the anchor (it read the prior-Term elevated reached rate as roughly 18%, which matches the pooled 17.2%). It also noticed the conceded circuit split and that the BIO raises vehicle problems.

Wrong, and this is what drives the number: the upward adjustment from 18% to 40%. The candidate treats the two distributions as two relists ("relist_bucket=2") and lifts the statpack's relist-count table's bucket-2 grant family rate (27.8% granted + 13.1% GVR ≈ 41%) as if it were the forward conditional for this petition. The statpack's own caveat on that table says the stored count is an upper bound on true relists because a reschedule before first consideration also adds a distribution entry, and this docket is exactly that shape: the May 5 distribution was superseded three days later by a call for a response, and the June 17 entry is the petition's first distribution for actual consideration. No relist in the substantive sense had occurred. The table is also a terminal-bucket cut (where petitions ended), not a hazard from a given count, and the `sal-v4` elevated band already conditions on the trajectory, so adding the two rates double-counts the same distributions. The Court then denied at its first full conference, which is what the docket's shape implied.

The second gap is that the "vehicle problems" the candidate names are the subjective-expectation-of-privacy record and the non-dispositiveness of the evidence. It never mentions the BIO's lead argument, the 28 U.S.C. § 1257(a) finality objection to an interlocutory state suppression ruling on remand, which is the strongest downward signal in the record and the one the other analyses of this petition treat as decisive. A three-sentence rationale that misreads the one docket signal it leans on and omits the record's main threshold problem is thin for a number more than double the anchor.

Small self-report inconsistency, not leakage: `retrieval.md` says "No retrieval beyond the provisioned inputs and the local statpack," but the log carries one `fedcourts query` shell call with structured filters (result unobserved). The pipeline's prior-availability note already weighs self-report against capture, so I note it here and do not flag it.

## Reasoning quality: 0.30

Correct anchor and correct label, but the one substantive adjustment rests on a misread of the distribution history and a misuse of a terminal table, and the analysis misses the record's central jurisdictional defect. Scored on soundness: the 0.40 was not well supported by the materials the candidate had.

## Leakage

`mode` forward; `retrieved_outcome_material` false; `influenced_prediction` not_applicable; `leakage_suspected` false. The prediction was created 2026-09-16 from the 2026-09-15 snapshot, when the petition stood distributed for the 2026-09-28 conference, so the case was genuinely open; not a mis-provisioned decided case. Log: 24 calls, every one `unobserved` (`result_capture_coverage` 0.0, the engine's standing shape, not a defect), so each is graded on its query: directory listings and file reads of the provisioned record and the prompt, greps of the petition and BIO for "split", a read of `metrics/statpack.md`, one corpus query with era and disposition filters, the output writes, and a `validate` run. No web search, no CourtListener call, no query naming this petition's disposition, no retrieved document dates, nothing under `data/qp-topics/`. The `not_applicable` grade rests on the log's queries and the reasoning, since no results were captured and the candidate's `flags.json` is not staged.

## Big case

My independent read is 0.45. The underlying question (whether an officer may open a hash-matched CyberTip file no human at the provider has viewed) is a genuine, respondent-conceded, six-circuit split governing a nationwide investigative pipeline, and a grant would have been a significant Fourth Amendment case. The vehicle was an interlocutory state criminal suppression ruling with a facial finality defect, one amicus, no CVSG, and a silent denial. Big issue, modest case. Disclosure: I printed the staged `prediction.json` files whole before writing, so the predictor's `big_case_score` was visible before I fixed my number; the read above is formed from the record.
