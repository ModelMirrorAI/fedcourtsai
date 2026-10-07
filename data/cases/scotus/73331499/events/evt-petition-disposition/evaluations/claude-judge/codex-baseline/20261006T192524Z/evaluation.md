# Evaluation — codex-baseline, scotus/73331499 (Williams v. Pennsylvania, No. 25-1277), evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition was distributed once (June 24, 2026, for the September 28 long conference) and **denied on October 5, 2026**, with no noted dissent (`outcome.json`: `actual_disposition` `denied`, `actual_granted` 0, `distribution_count` 1).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.08 − 0)² = **0.0064**.
- `segment_base_rate` = **0.0512**, basis `risk_set`. The prediction froze `band` `baseline` under `salience_version` `sal-v4`, Term 2025, and the statpack's segment table heading is `sal-v4`, so the versions match. Pooled the bracketed `reached` baseline figures over every rendered Term strictly before 2025 (OT2017–OT2024, eight rows), resolved-weighted: ≈592.9 / 11,580 = 5.12%. The table renders 10 of 10 Terms, so the rendered window is the pack's whole window and no lookback divergence arises. (The candidate computed the same 5.12% itself.)
- `brier_skill_score` = 1 − 0.0064 / 0.0512² = **−1.441**. The forecast sat above the band baseline on a petition that was denied, so a naive baseline forecaster would have scored better.
- `vote_accuracy`, `judgment_correct`: omitted / null (cert stage).
- `claim_scores`, `process_version`, `base_rate_salience_version`, `prediction_run_id`: left to the harness.

## Leakage

Mode `forward`; the case was open on September 16, 2026, when the prediction was made, and resolved October 5. The captured log (30 calls, coverage 0.93) shows local reads, two hosted web-search calls whose results were `unobserved` (graded on their queries: State v. Belt and State v. Police, general authorities, not this petition), and CourtListener opinion lookups of Belt and Police. No call targets this docket, no `retrieved_doc_date` on or after the resolution, no read under `data/qp-topics/`. The reasoning states it sought nothing about this petition's disposition and the log agrees. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Reasoning quality — 0.65

A careful and transparent rationale whose central judgment went the wrong way.

What it does well:

- **Correct anchor, shown step by step.** Reads the frozen band and version, pools the eight prior-Term reached rows by their weighted denominators to 5.12%, excludes the case's own Term, and says explicitly that the relist and CVSG cuts are terminal and are not transplanted into the increment claims.
- **Primary-source verification.** It checked the Belt and Police passages on CourtListener rather than taking the petition's characterization, and reported what the passages actually say. That is the right instinct for a conflict claim.
- **Honest information boundary.** It states that the snapshot's silence on a response or waiver is a statement about supplied entries, declines to assume a waiver or a procedural bar the record does not establish, flags the truncated Question 2 rather than completing it, and lists its limitations.

Why the score is not higher: the one directional call the rationale makes, moving **up** from the 5.1% anchor to 8%, is poorly supported by its own evidence and was not borne out. The uplift rests on a published intermediate-court decision and a "concrete" Belt comparison on a John Doe DNA warrant particularity question that the candidate itself describes as turning on unusual historical facts and an unverified conflict. Against that it lists, but underweights, the facts that actually govern a one-distribution paid petition: no brief in opposition (so a grant would first require a call for a response), no amici, intermediate state court, and a QP 2 the Court would have to rewrite. The rationale never prices the no-BIO structure as a two-step path, which is what caps the probability well below the band rate. The hedge that "the absence of a response is not proof that no omitted filing exists" is also overcautious: a waiver appears on the Supreme Court docket as its own entry, and none was there. The result is a thorough, well-sourced analysis that ends a few points on the wrong side of the baseline, and a negative skill score for it.

## Stakes read (`big_case`)

My independent read is **0.35**. The shed-DNA / forensic-genetic-genealogy question is recurring and would matter if decided, but this case carried none of the markers of a big case: paid petition from a state intermediate court, no BIO, no amici, one distribution, a silent long-conference denial. The stakes are in the issue, not in this vehicle. The staged `prediction.json` lists the predictor's `big_case_score` near the top, so that number was visible before I formed this read; the read is from the record, not from it.
