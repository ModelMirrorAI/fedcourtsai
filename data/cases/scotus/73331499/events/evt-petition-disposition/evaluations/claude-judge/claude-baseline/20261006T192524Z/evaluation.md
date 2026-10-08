# Evaluation — claude-baseline, scotus/73331499 (Williams v. Pennsylvania, No. 25-1277), evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition was distributed once (June 24, 2026, for the September 28 long conference) and **denied on October 5, 2026**, with no noted dissent (`outcome.json`: `actual_disposition` `denied`, `actual_granted` 0, `distribution_count` 1).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.025 − 0)² = **0.000625**.
- `segment_base_rate` = **0.0512**, basis `risk_set`. The prediction froze `band` `baseline` under `salience_version` `sal-v4`, Term 2025, and the statpack's segment table heading is `sal-v4`, so the versions match. Pooled the bracketed `reached` baseline figures over every rendered Term strictly before 2025 (OT2017–OT2024, eight rows), resolved-weighted: ≈592.9 / 11,580 = 5.12%. The table renders 10 of 10 Terms, so the rendered window is the pack's whole window and no lookback divergence arises.
- `brier_skill_score` = 1 − 0.000625 / 0.0512² = **+0.762**. The forecast beat the band baseline comfortably.
- `vote_accuracy`, `judgment_correct`: omitted / null (cert stage).
- `claim_scores`, `process_version`, `base_rate_salience_version`, `prediction_run_id`: left to the harness.

## Leakage

Mode `forward`; the case was genuinely open on September 16, 2026, when the prediction was made, and resolved October 5. The captured log (30 calls, coverage 1.0) shows local reads, two `fedcourts query` calls, and six CourtListener lookups. The docket lookup returned `date_terminated` null and `date_modified` 2026-06-24, i.e. the pre-decision docket, and the docket-entries call returned nothing. No `retrieved_doc_date` on or after the resolution, no query reaching past the event date, no read under `data/qp-topics/`. The reasoning reads the outcome off nothing. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Reasoning quality — 0.85

This is the strongest of the three rationales. What drives the score:

- **Correct anchor, correctly derived.** It read the frozen band and version, confirmed the table heading matched, pooled the reached figures over the eight prior Terms (n = 11,580, ≈5.1%), and excluded the case's own Term. It also read the relist and CVSG cuts but labelled them terminal and used them for shape only, which is the right discipline.
- **The structural argument is the right one.** With no brief in opposition and no waiver on the docket, a grant requires a call for a response first, then a grant after the response. Decomposing P(grant) as P(CFR) × P(grant | CFR) ≈ 0.13 × 0.15 and landing near 0.02 to 0.03 is a sound way to price a one-distribution, no-BIO petition, and the outcome (silent denial on the first order list) bore it out.
- **Vehicle analysis is specific and accurate to the record.** Intermediate state court with discretionary review declined; QP 1 fact-bound to a 2000 John Doe complaint listing six RFLP loci; the petition's own survey of Belt / Police / Robinson / Boughton / Burdick / Carlson read as fact-pattern divergence rather than a doctrinal split; QP 2 truncated mid-sentence (it is: "the creation of DNA profiles from."); no amici, no CVSG; the Court's prior refusal to take the abandoned-DNA question from Maryland (Raynor). Each point is grounded in the provisioned material and each cuts the right way.
- **Honest uncertainty section.** It says the Superior Court opinion was not available, that the anchor rests on the statpack alone because the corpus queries returned non-comparable rows, and that nothing about the outcome was encountered.

What keeps it below the top of the scale: the upward adjustment paragraph is thin relative to the downward list, and the 20% second-distribution hazard (mostly a response request) was generous for a petition the Court denied outright, though that number is a claim scored in code and does not enter this grade. The rationale's net call, a 2.5% grant forecast on a petition that was denied silently, is well calibrated.

## Stakes read (`big_case`)

My independent read is **0.35**. The shed-DNA / forensic-genetic-genealogy question is recurring and would matter if decided, but this case carried none of the markers of a big case: paid petition from a state intermediate court, no BIO, no amici, one distribution, a silent long-conference denial. The stakes are in the issue, not in this vehicle. The staged `prediction.json` lists the predictor's `big_case_score` near the top, so that number was visible before I formed this read; the read is from the record, not from it.
