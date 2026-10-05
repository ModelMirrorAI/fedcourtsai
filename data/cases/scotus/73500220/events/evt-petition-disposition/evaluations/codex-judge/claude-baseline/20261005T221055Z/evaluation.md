# Evaluation — claude-baseline

Case: scotus/73500220; event: evt-petition-disposition; evaluation run:
20261005T221055Z. The blinded prediction is from run 20260917T181231Z.

## Outcome and quantitative assessment

The authoritative `outcome.json` records **denied**, `actual_granted: 0`,
resolved October 5, 2026. The provisioned October 5 snapshot also contains
that day's denial entry. The September 17 prediction called **denied** with
P(grant) = 0.02, so exact-label correctness is **1** and Brier is
(0.02 - 0)^2 = **0.0004**. Against the baseline below, Brier skill
is 1 - 0.0004 / (0.05120250431778929 - 0)^2 = **0.847427035177**.

## Reasoning quality: 0.73

The rationale correctly conditions on the private-petitioner baseline risk
set and makes a transparent downward adjustment for the response waiver,
limited indications of Court interest, and the asserted split's imperfect
fit to civil FCA liability. It separates disagreement in reasoning from a
square conflict over this consequence, acknowledges the incomplete source
review and failed verification attempt, and leaves room for a call for
response. Those features support a low grant estimate independently of the
realized denial.

The principal substantive omission is the separate nonretroactivity holding
in the supplied petition's Appendix A, pp. 14–16. The appended opinion
expressly adopts that alternative ground, not merely a generic collateral-
review concern. claude-baseline discusses section 2255 and possible prejudice
problems without identifying this obstacle, and presents an alternative
performance ground as something the lower court could have used rather than
fully accounting for its actual alternative holdings. Appendix A, p. 13
n.3 also supplies the FCA-specific alternative ground. The candidate's
statement that the legal question is cleanly presented therefore needs
qualification. Its broad claim about repeated denials of other Padilla
extensions is not supported with identifiable examples in the rationale;
the asserted counsel-profile signal likewise receives little substantiation.
These are analytical limitations, not conclusions that the denial establishes
those propositions false. The appendix passages are available in the staged
petition notwithstanding its overall truncation.

## Leakage assessment

The captured log records forward mode, September 17 calls, and result capture
coverage of 1.0 (20/20 calls). The target-caption search sought lower-court
material; the retrieval note reports throttling. The corpus query sought
other granted cases. The record does not show the October 5 denial or other
outcome-revealing target material reaching the prediction. Its rationale
still treats the September 28 conference and eventual disposition as future.
Accordingly, retrieved outcome material is false, influence is
`not_applicable`, and leakage suspected is false. Capture markers and query
content support this finding; null retrieved-document dates are not treated
as proof that searches returned nothing.

## Baseline and scoring scope

This is a cert-stage event. The frozen prediction context records Term 2025,
`baseline`, and `sal-v4`; the committed `metrics/statpack.md` segment heading
also records `sal-v4`. I use the bracketed **reached** population and record
`base_rate_basis: risk_set`, not the terminal band or the evaluator's context.
All eight displayed Terms strictly before 2025 enter the pool: 2024 (5.7%,
n=1271), 2023 (5.9%, n=1312), 2022 (5.8%, n=1192), 2021 (5.6%, n=1500),
2020 (4.5%, n=1739), 2019 (4.6%, n=1399), 2018 (4.6%, n=1524), and 2017
(4.7%, n=1643). Terms 2025 and 2026 are excluded. The table renders 10 of
10 Terms, so there is no rendered-window omission to flag.

Pooling the displayed, rounded percentages gives 592.925 / 11580 =
**0.05120250431778929**. This numerator is a weighted approximation, not an
integer grant count. The baseline and skills inherit the rendered table's
rounding and denial reweighting. I use the committed artifact as supplied;
no live corpus refresh or underlying corpus-wide vintage is asserted.
Positive skill here describes this single denial relative to that baseline,
not established calibration or aggregate forecasting performance.

Only `reasoning.md` enters reasoning quality. The pointed-to
`predicted_reasoning.md` was read for context but not graded; quantitative
claims are left to the harness. No vote accuracy or semantic grades are
written on this cert cell. A denial supplies no merits holding or explanation
of the Court's reasons.
