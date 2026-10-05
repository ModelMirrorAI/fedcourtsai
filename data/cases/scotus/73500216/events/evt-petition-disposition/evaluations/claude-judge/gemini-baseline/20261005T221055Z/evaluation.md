# Evaluation: gemini-baseline — scotus/73500216, evt-petition-disposition

## Cell and outcome

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`), forward mode. The petition (No. 25-1316, Pearson v. Guerrero) was distributed once, for the 2026-09-28 long conference, and **denied on 2026-10-05** with no noted dissent (`actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`).

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.01 − 0)² = 0.0001.
- `segment_base_rate` = 0.0512, `base_rate_basis` = `risk_set`. The prediction's frozen context carries `band: baseline` **and** `salience_version: sal-v4`, and the committed `metrics/statpack.md` "Segment base rate by salience band" heading names `sal-v4`, so the bracketed `reached` figure applies. Pooled resolved-weighted over the rendered Terms strictly before this case's Term 2025 (OT2017–OT2024; the 2026 row is empty and 2025 is the case's own Term): 592.9 / 11,580 ≈ 0.0512. The caption says 10 of 10 Terms are rendered, so the rendered window is the pack's whole window and there is no window divergence to flag.
- `brier_skill_score` = 1 − 0.0001 / 0.0512² ≈ 0.9619.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: omitted — cert stage.

## Reasoning quality: 0.55

What is sound: the candidate anchors on the right table and the right figure ("roughly 5%" for a `baseline` paid petition, pooled prior-Term), identifies the dominant obstacle correctly (a section 2254(d)(1) posture in which the asserted rule descends from a concurrence in *Smith v. Phillips* and a circuit split, so a state court cannot have unreasonably applied clearly established law), and reads the single distribution as pointing to a prompt first-conference denial. Its direction and rough magnitude of adjustment were vindicated.

What costs it: (1) **An invented docket fact.** The rationale states the respondent "waived its right to file a Brief in Opposition." The snapshot carries no waiver entry: the docket shows the petition filed with a response due 2026-06-29, then distribution on 2026-07-15, and nothing from the respondent at all. The other two candidates read the same snapshot and correctly reported neither a response nor a waiver. The inference drawn (no opposition on file) happens to hold, but the fact asserted is not in the record, and the contract is never to invent facts. (2) **AEDPA is overstated as categorical.** The Fifth Circuit, as the petition's Appendix A shows, *assumed arguendo* that implied bias is clearly established and held the facts outside the "extreme genre"; the vehicle problem is real but is a reasonableness holding on thin juror-specific facts, not the flat impossibility the rationale describes. (3) **Thinness.** No engagement with the quality of the asserted split, the unpublished opinion below, the voluntary disclosure and "thought she could be fair" facts, or the Strickland layer. The corpus query failed and the candidate said so honestly, which is fine, but nothing replaced it.

The number (0.01) is defensible and scored best on this cell, but the write-up supports it less carefully than the other two candidates support theirs.

## Leakage

`mode: forward`, `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. The prediction was created 2026-09-17, eleven days before the conference and eighteen before the denial, against a snapshot whose last entry is the 2026-07-15 distribution; the case was genuinely open. The log's 27 calls all carry `result_capture: unobserved` (`result_capture_coverage` 0.0, the engine's standing shape), so every call is graded on its query: provisioned record reads, four statpack greps, one failed corpus query for prior denials, and output writes. No call names this docket's disposition, no web or CourtListener call was made, and no `data/qp-topics/` path appears. The reasoning treats the case as pending. Not a mis-provisioned decided case.

## Big case

My own read is 0.22 (see `big_case.notes`). The predictors' scores sat inside the staged `prediction.json`, which I had read before writing mine down, so the independence of this read is partial.
