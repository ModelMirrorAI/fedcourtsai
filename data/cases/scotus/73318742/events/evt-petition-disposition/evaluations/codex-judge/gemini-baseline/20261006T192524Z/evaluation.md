# Evaluation: gemini-baseline

## Outcome and quantitative scores

This is a cert-stage petition-disposition event. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`; the provisioned October 5 snapshot independently contains the denial entry. gemini-baseline predicted `denied` with P(any grant) = 0.01. Consequently, `correct = 1` and Brier = (0.01 - 0)^2 = **0.0001**. The denial supplies no explanation adopting either party's legal theory.

The prediction freezes Term 2025, band `baseline`, and `sal-v4`. These match the committed statpack's sal-v4 table. I use its bracketed **reached** rates, resolved-weighted over all rendered Terms strictly before 2025: 2017–2024. In ascending Term order, the rate/denominator pairs are 4.7%/1643, 4.6%/1524, 4.6%/1399, 4.5%/1739, 5.6%/1500, 5.8%/1192, 5.9%/1312, and 5.7%/1271. Their weighted denominator is 11,580 and the pooled rate is **0.05120250431778929**, with `base_rate_basis = risk_set`. These are denial-reweighted estimates reconstructed from rounded published cells, not exact underlying grant counts. The skill calculation is 1 - 0.0001 / baseline^2 = **0.961856758794282**.

The table renders 10 of 10 available Terms; no hidden-window divergence or version mismatch arises. Terms 2025 and 2026 are excluded. The baseline uses the scored prediction's context, not the evaluator's decided-docket context. This describes the committed statpack supplied to the cell, not a refreshed live corpus; I did not query a corpus blob or establish its vintage. This single-event skill value is not an aggregate performance claim.

## Reasoning quality: 0.62

The analysis identifies the basic immunity-versus-disqualification theory and gives a plausible downward adjustment from the appropriate prior-Term baseline. It focuses on the absence of a demonstrated circuit split rather than mistaking a filed opposition or the summer wait for positive Court interest. Its denial forecast is consistent with the recorded result, but correctness alone does not establish sound analysis.

The justification is thin and unusually categorical. Calling the petition frivolous and assigning virtually zero prospect of review substitutes labels for examination of the proposed doctrinal extension. It does not distinguish judicial immunity from the official-capacity sovereign-immunity and remedial barriers described in the opposition, or evaluate the opposition's specific preservation objection. The petition describes the affirmance as solely based on judicial immunity, while the opposition describes additional grounds; the rationale neither identifies nor manages that evidentiary conflict. It also gives no clear account of why the proposed due-process exception fails to create a suitable vehicle beyond saying existing immunity is well established. These omissions, not the eventual denial, drive the moderate score.

Only `reasoning.md` receives this qualitative score. I read the forecast document for context but do not score it, the quantitative claims, or their realized procedural details. No vote score or semantic grading is appropriate on this cert event; mechanical claim scores remain the harness's responsibility. I omit the optional independent significance assessment.

## Leakage assessment

The harness log records forward mode and 26 calls on September 16, before the October 5 resolution. Its local reads concern the provisioned snapshot and documents, and the prose does not presuppose denial. The corpus query `uv run fedcourts query --court scotus --decided-before 2026-09-17` is not a search for this petition's result and predates that result. All result markers are unobserved: capture coverage is 0.0. I therefore assess query scope and chronology rather than treating absent result dates as proof that nothing returned.

There is no affirmative evidence of outcome material or mis-provisioning of an already-decided case. I record `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`, with the telemetry limitation stated explicitly. The retrieval note omits the logged corpus-query attempt despite claiming no retrieval beyond local materials. A cell-level informational flag records that discrepancy; whether the query succeeded or transferred data is unknown. It is not evidence of leakage and does not alter the computed scores.
