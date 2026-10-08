# Evaluation of claude-baseline — Cohen v. Judicial Conduct Board of Pennsylvania (No. 25-1215), evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition was **denied** on 2026-10-05 after the September 28 long conference, with no noted dissent and no distribution beyond the two already on the docket (`actual_granted` 0, `distribution_count` 2).

- `correct` = 1: `predicted_disposition` `denied` matches `actual_disposition` `denied`.
- `brier_score` = (0.16 − 0)² = **0.0256**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The prediction's frozen context carries `band` `elevated` with `salience_version` `sal-v4`, matching the statpack table's heading, so the bracketed `reached` figure applies. Pooled resolved-weighted over the rendered Terms strictly before Term 2025 (2017–2024, the 2026 row being empty): 484.4 / 2810 = 0.1724. The caption shows 10 of 10 Terms, so the rendered window is the pack's and there is no lookback divergence to flag.
- `brier_skill_score` = 1 − 0.0256 / 0.1724² = **0.138**. Modestly better than the band baseline: the forecast moved below the anchor, in the realized direction.

## What the prediction got right and wrong

Right: the disposition, the direction of the adjustment, and nearly every qualitative call. The candidate predicted a clean denial on the October 5 order list with no further distribution, no CVSG, and most likely no separate writing; all of that happened. Its baseline work is exactly the contract's: the matching sal-v4 table, the bracketed reached figure, Terms 2017–2024, the weighted n, and an explicit refusal to use the terminal two-distribution relist bucket for a petition that had not ended.

The most valuable piece of analysis is the band-sourcing observation. The candidate noticed that the `elevated` band under sal-v4 derives from a distribution count of two, that the first distribution was overtaken by the May 12 call for a response, and that the second is a routine post-response redistribution rather than a relist, so the band credits a relist that never happened, while the response request itself goes unread by the band. It then treated the two as roughly offsetting and kept the anchor. That is a careful, correct reading of what the frozen context does and does not encode, and the only candidate to state it. I have carried it into this cell's `flags.json` as an info note.

Where it could have been sharper: 0.16 is only one point below the anchor. The candidate's own downward list — alternative strict-scrutiny holding below, trappings-of-office facts, a retired petitioner, a contestable split, unattractive facts, no amici, and a consistent record of denials in the judicial-discipline speech cases the petition itself cites — reads as considerably stronger than its upward list, and a reader following the argument would expect a larger discount. The candidate acknowledged this by saying where to discount it.

## Reasoning quality: 0.85

Strengths: the fullest and most balanced legal analysis of the three. It used the whole provisioned record (BIO in full, the petition's argument section, the QP), named the specific vehicle problems with reference to how the Court actually behaves on them, treated the Scott v. Flowers point about Fifth Circuit panel precedence as credible rather than dispositive, and tied each secondary number to a stated mechanism. The uncertainty section is honest about what was not read (the reply) and what rests on general knowledge rather than a committed cut (the strength of a call for response). The CourtListener docket check was a legitimate forward confirmation that the case was still open, not a search for an outcome.

What held it down: the number did not follow the weight of the argument, and one factual claim — that the grant share is higher at the long conference — is asserted without a source and is contested by another candidate; neither side cites evidence, so I did not credit or penalize it. A few cert-process judgments (the clinic's decision to take the opposition as a positive signal) are plausible but unquantified.

## Leakage

Mode `forward`; the case was pending at the 2026-09-17 snapshot and resolved 2026-10-05. The log's 30 calls are fully captured. The corpus citation query (a `retrieved_doc_date` of 2025-02-11, a prior case) returned no rows; the CourtListener docket lookup (`retrieved_doc_date` 2026-04-24, the filing date) returned `date_terminated` null and last-modified 2026-08-03, confirming the petition was undecided; the docket-entries and topical search calls returned nothing. No date on or after resolution, no `data/qp-topics/` path, no outcome reference in the prose. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Big case

My independent read is 0.35: a real doctrinal question for sitting judges nationwide, invited by the court below, but carried by a retired petitioner, a six-rule sanction with trappings-of-office facts, no amici, and a silent denial. Moderate stakes if granted, low public salience, weak vehicle. The predictor's score sits in the staged `prediction.json`, so I had seen it before writing this; the read rests on the record.

## Not scored here

`claims`, `predicted_reasoning.md`, and the noted-vote fields are outside this grade by contract; `claim_scores`, `process_version`, and `base_rate_salience_version` are the harness's.
