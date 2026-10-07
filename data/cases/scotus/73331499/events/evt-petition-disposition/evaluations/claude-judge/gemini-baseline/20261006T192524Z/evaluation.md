# Evaluation — gemini-baseline, scotus/73331499 (Williams v. Pennsylvania, No. 25-1277), evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition was distributed once (June 24, 2026, for the September 28 long conference) and **denied on October 5, 2026**, with no noted dissent (`outcome.json`: `actual_disposition` `denied`, `actual_granted` 0, `distribution_count` 1).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.015 − 0)² = **0.000225**.
- `segment_base_rate` = **0.0512**, basis `risk_set`. The prediction froze `band` `baseline` under `salience_version` `sal-v4`, Term 2025, and the statpack's segment table heading is `sal-v4`, so the versions match. Pooled the bracketed `reached` baseline figures over every rendered Term strictly before 2025 (OT2017–OT2024, eight rows), resolved-weighted: ≈592.9 / 11,580 = 5.12%. The table renders 10 of 10 Terms, so the rendered window is the pack's whole window and no lookback divergence arises.
- `brier_skill_score` = 1 − 0.000225 / 0.0512² = **+0.914**, the best of the three on this cell.
- `vote_accuracy`, `judgment_correct`: omitted / null (cert stage).
- `claim_scores`, `process_version`, `base_rate_salience_version`, `prediction_run_id`: left to the harness.

## Leakage

Mode `forward`; the case was open on September 16, 2026, when the prediction was made, and resolved October 5. The captured log (25 calls) has `result_capture_coverage` 0.0, which is this engine's standing shape rather than a defect, so every call is graded on its query: reads of the prompt, `AGENTS.md`, `event.yaml`, `context.json`, the 2026-09-16 snapshot, the documents manifest and QP, the statpack, and one `fedcourts query --court scotus --era roberts`. No external lookup of any kind, nothing under `data/qp-topics/`, and no call that could have reached this petition's disposition. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Reasoning quality — 0.55

A short rationale that lands on the right structural point but does little work to get there.

What is sound:

- **The governing structure is identified.** No brief in opposition before distribution, so a call for a response would be required before any grant; one distribution for the long conference; a state criminal petition. That is the core of why this petition was denied, and the candidate says it.
- **The absence of a split is read correctly from the QP**, which itself frames both questions as "issues of first impression to this Court," and the Greenwood abandonment doctrine is the right doctrinal headwind for the trash-DNA question.
- **The number is well calibrated** to the outcome and sits sensibly below the band rate.

What holds the score down:

- **The anchor is approximate rather than computed.** "~5.5% (reached)" is roughly the recent-Term reached rates, not the strictly-prior pooled figure (5.1%); the difference is small here but the method is not shown.
- **One factual inference overreaches.** It says the missing BIO indicates Pennsylvania "likely waived its right to respond." A waiver is its own docket entry, and the snapshot shows none; the record shows only that no response was filed by the due date. The conclusion (CFR needed before grant) survives either way, but the premise is not in the record.
- **No engagement with the petition's actual conflict claims.** The petition cites Belt, Police, Davis and Raynor; the rationale does not mention or assess any of them, so the "no developed split" conclusion is asserted from the QP's own framing rather than tested against the petition's argument. The two other candidates both did that work.
- **No decomposition and no stated uncertainty.** The 1.5% is a bare number; there is no CFR-path arithmetic, no discussion of what would move it, and no limitations section.

In short: right answer, right headline reason, thin analysis.

## Stakes read (`big_case`)

My independent read is **0.35**. The shed-DNA / forensic-genetic-genealogy question is recurring and would matter if decided, but this case carried none of the markers of a big case: paid petition from a state intermediate court, no BIO, no amici, one distribution, a silent long-conference denial. The stakes are in the issue, not in this vehicle. The staged `prediction.json` lists the predictor's `big_case_score` near the top, so that number was visible before I formed this read; the read is from the record, not from it.
