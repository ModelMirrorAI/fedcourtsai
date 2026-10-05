# Evaluation: codex-baseline

Case `scotus/73358594`, event `evt-petition-disposition`; cert stage. The authoritative outcome records **denied**, `actual_granted = 0`, resolved October 5, 2026. This evaluates the blinded September 16, 2026 prediction, run `20260916T201911Z`.

## Quantitative result

- Predicted disposition: **denied**; exact-match `correct = 1`.
- P(any grant): **0.015**; Brier = (0.015 - 0)^2 = **0.000225**.
- Baseline: **0.05120250431778929**, using the frozen-band risk set.
- Brier skill = 1 - 0.000225 / (0.05120250431778929 - 0)^2 = **0.9141777072871347**.

The positive skill value describes this one denied case relative to its baseline, not population-level calibration or demonstrated general forecasting skill.

## Reasoning quality: 0.90

The headline rationale is carefully tied to the provided facts: a private petitioner despite a federal respondent, one distribution rather than a relist, a waived response, and a nonprecedential Rule 36 affirmance. The staged petition supports the distinction between an allegedly unaddressed gross-mismanagement theory and a demonstrated conflicting legal rule. The candidate treats the petition's allegations as advocacy rather than findings and acknowledges both the petition's procedural analogy to Flynn and the possible alternative same-action rationale. Those are meaningful counterweights rather than reasons manufactured from the denial.

The candidate starts with the appropriate frozen-band risk-set population and explicitly distinguishes terminal relist/circuit cuts from a forward probability. Its move from roughly 5.12% to 1.5% is identified as judgmental, not estimated from a fitted waiver-case model. This makes the reasoning auditable without pretending the observed denial validates that exact probability.

The remaining limitations are incomplete administrative-record review, unresolved preservation and outcome-determinacy issues, and the absence of a quantified basis for the size of the downward adjustment. The candidate acknowledges them rather than claiming certainty. The high score rewards this evidentiary discipline in `reasoning.md`, not its forecast document or ancillary claim probabilities.

## Baseline and scoring scope

All dates and facts here refer to the provisioned record, not a newly refreshed corpus. The prediction froze Term 2025, band `baseline`, and salience version `sal-v4`. The matching heading in committed `metrics/statpack.md` supports `base_rate_basis: risk_set`. I use the bracketed **reached** rates, weighted by their displayed resolved denominators, from every displayed strictly prior Term: OT2017–OT2024. OT2025 and OT2026 are excluded. The eight denominators sum to 11,580; multiplying them by the rounded displayed rates gives a weighted numerator of 592.925 and an approximate baseline of 0.05120250431778929 (5.12025%). This fractional numerator is a calculation from rounded rates, not an observed integer grant count. The caption renders 10 of 10 Terms, so there is no rendered-window truncation to flag. No current corpus vintage was established or claimed.

The cert-stage disposition comparison and binary Brier are separate from analysis quality. Vote accuracy and semantic grades are inapplicable on this cert event and are omitted. Quantitative claims remain for the harness; neither those claims nor `predicted_reasoning.md` receive a score here. The latter was read only for context. Denial establishes the outcome, not the Court's reasons or the correctness of the petitioner's underlying legal position. The staged petition's manifest reports truncated text from a 194-page PDF; neither this evaluation nor the candidates' partial reads establish a complete administrative-record review.

## Leakage assessment

The captured log records 31 calls, 29 with captured results (coverage 0.9354838709677419). Its two unobserved web rows concern general certiorari rules and a rules PDF; I do not treat the candidate's report of no usable content as a captured fact. Other retrieval consists of a historical citation search and a passage lookup, alongside local inputs and scoring context. Nothing in the query slices or rationale shows this case's October 5 disposition surfacing before prediction. The forward prediction preceded that disposition, so `retrieved_outcome_material` is false, `influenced_prediction` is `not_applicable`, and `leakage_suspected` is false. Null document dates alone are not the basis of that conclusion.

## Independent significance assessment

Score **0.30**, formed from the question presented and outcome before viewing the candidate scores. The completeness of federal whistleblower adjudication could matter beyond this employee, but the record presents a comparatively narrow omitted-theory dispute. The score does not measure grant probability or agreement with the candidate, and the denial does not supply a merits holding.
