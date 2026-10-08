# Evaluation: gemini-baseline

## Outcome and numerical scores

This is a cert-stage petition-disposition event. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`; the October 5 snapshot independently contains the denial entry. The candidate predicted `denied` with P(any grant) = 0.01, so exact-label correctness is 1 and the Brier score is `(0.01 - 0)^2 = 0.0001`. A correct denial forecast does not establish why the Court denied review or endorse either party's substantive position.

The scored baseline comes from the candidate's frozen `context.band = baseline`, `salience_version = sal-v4`, and docket Term 2025, not the evaluator's decided-docket context. The matching committed statpack table supplies the bracketed reached-baseline rates. Pooling all displayed strictly-prior Terms, 2017–2024, gives weighted denominator 11,580 and rate 0.05120250431778929. In descending Term order, the inputs are 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643. These are denial-reweighted live/historical-slice estimates, and the rate is approximate because published percentages are rounded. The table renders 10 of 10 Terms; there is no hidden-window truncation. Own-Term 2025 and later-Term 2026 are excluded. The basis is `risk_set`; skill is `1 - 0.0001 / 0.05120250431778929^2 = 0.961856758794282`.

These figures describe the committed statpack supplied to this run, not freshly queried remote corpus state. No corpus-wide freshness claim is made.

## Reasoning quality: 0.60

The rationale identifies relevant observed features: a waived response, no recorded response request, and a fact-specific third question presented. Its direction of adjustment is intelligible and does not assume that an academic-freedom question alone guarantees review. It appropriately forecasts a petition disposition rather than treating a grant as a merits victory.

Its support is nevertheless thin. It anchors on the current Term's 3.9% rate rather than the prescribed strictly-prior pooled rate. That is a baseline-selection weakness, not evidence of outcome leakage in an open forward cell. It treats the respondents' waiver as proof that they consider the petition meritless and do not fear review; the recorded waiver alone does not establish those motives. The rationale does not develop the petition's own description of the appellate causation ground or its concession that the asserted split is not precisely the proposed question. Those record-specific points would support the vehicle assessment more directly than labeling the dispute fact-bound. The move to exactly 1% is judgmental rather than supported by a comparable conditional sample.

The score evaluates the soundness of `reasoning.md`, not brevity, the fortunate low Brier score, the separate forecast document, or the quantitative claims. The unexplained denial does not retrospectively validate the candidate's inferred respondent motives.

## Leakage and scoring limits

The harness log labels the prediction forward. Its September 17 call timestamps and stated forecast precede the October 5 resolution. The log shows provisioned-input reads, committed-statpack access, and broad SCOTUS corpus queries. No query seeks this petition's outcome, and the prose does not cite a disposing order or speak as though denial had already occurred.

All 25 log entries have unobserved results, with capture coverage 0.0. I assess their queries and the staged prose; I do not interpret absent result dates or digests as proof that calls returned nothing. There is no affirmative evidence of this case's outcome material, so `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`, subject to that telemetry limit. Missing staged predictor flags are not evidence of cleanliness.

Cert votes are unscored, and no semantic grade set applies. The forecast was read for context only. Mechanical claim scores and provenance/context stamps are left to the harness. No independent big-case assessment is supplied.
