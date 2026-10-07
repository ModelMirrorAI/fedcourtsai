# Evaluation: gemini-baseline

## Outcome and quantitative scores

This is a cert-stage evaluation of the prediction from run `20260918T174135Z`. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`. The predicted label was `denied`, so correctness is **1**. With P(grant) = 0.07, the Brier score is `(0.07 - 0)^2 = 0.0049`.

The baseline uses this prediction's frozen `context.band = elevated`, `salience_version = sal-v4`, and docket Term 2025, not the evaluator's terminal context or the resolution's calendar year. The committed `metrics/statpack.md` table has the matching sal-v4 heading and renders 10 of 10 Terms. The eligible bracketed reached rows are OT2017–OT2024; OT2025 and OT2026 are excluded. Their displayed (rate, weighted resolved n) pairs, in descending Term order, are (17.9%, 336), (17.5%, 354), (19.0%, 300), (20.5%, 342), (16.1%, 397), (13.8%, 334), (15.9%, 347), and (17.5%, 400).

Pooling these printed rates gives `484.386 / 2810 = 0.17237935943060498`, with `base_rate_basis = risk_set`. The fractional numerator is a product of rounded displayed rates and denial-reweighted denominators, not a raw observed grant count. Brier skill is `1 - 0.0049 / 0.17237935943060498^2 = 0.8350981397274976`. This is a single-event comparison, not evidence of long-run calibration. These are committed-pack estimates, not a refreshed corpus claim; no live corpus freshness was obtained.

## Reasoning quality: 0.64

The rationale identifies two concrete reasons to discount grant probability: the unusual pandemic medical-risk setting and respondent's Rule 56 evidentiary objections. Those concerns are present in the provisioned opposition, especially its vehicle discussion on printed pages 21–23. It also starts from the appropriate reached-band population and acknowledges substantial amicus support. The correct denial prediction is not itself the reason for the qualitative grade.

The main analytical weakness is calling the alleged three-to-three split clean without confronting the opposition's central argument that the circuits share a standard and differ on the medical evidence. The provisioned opposition's introduction expressly disputes both the characterization of the decision below and the claimed conflict. Describing the split as established overstates an adversarial allegation. The categorical assertion that the Court has consistently denied pandemic-mandate cases is not substantiated in this rationale, and the move from roughly 17.5% to 7% is not supported by a measured conditional rate or a developed comparative analysis. The vehicle-based direction is intelligible, but its magnitude and the broader generalization are under-explained.

The outcome supplies no reason for denial, so it cannot verify that the Court accepted these vehicle arguments. The score grades only `reasoning.md`; the separately read forecast document and the quantitative claims are not graded here.

## Leakage and scoring boundaries

The prediction and all 30 logged calls precede resolution: September 18 versus October 5, 2026. Queries are limited to provisioned inputs, the statpack, and output/validation operations. All call results are marked `unobserved`, with capture coverage 0.0. This limits observability and is not evidence that calls returned nothing. Neither the query slices nor the prose shows this petition's disposition as already known. Accordingly, mode is `forward`, retrieved outcome material is false on the available evidence, influence is `not_applicable`, and leakage is not suspected. The unstaged predictor flags provide no evidence either way.

No cert votes are scored. No semantic set is declared for this stage. Mechanical claim scores and provenance stamps remain the harness's responsibility.
