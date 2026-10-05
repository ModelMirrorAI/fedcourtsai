# Evaluation — codex-baseline

Case: scotus/73500220; event: evt-petition-disposition; evaluation run:
20261005T221055Z. The blinded prediction is from run 20260917T181231Z.

## Outcome and quantitative assessment

The authoritative `outcome.json` records **denied**, `actual_granted: 0`,
resolved October 5, 2026. The provisioned October 5 snapshot also contains
that day's denial entry. The September 17 prediction called **denied** with
P(grant) = 0.015, so exact-label correctness is **1** and Brier is
(0.015 - 0)^2 = **0.000225**. Against the baseline below, Brier skill
is 1 - 0.000225 / (0.05120250431778929 - 0)^2 = **0.914177707287**.

## Reasoning quality: 0.94

The analysis connects the probability to the frozen private-petitioner risk
set, distinguishes respondent identity from petitioner class, excludes the
case's own and later Terms, and labels the downward adjustment judgmental
rather than fitted. Its unrounded 593/11580 anchor is reported as drawn from
the companion JSON; the tiny difference from this evaluation's rounded-
Markdown anchor is not a population or window disagreement.

Its strongest contribution is direct engagement with the appended lower-
court decision. Appendix A, pp. 14–16 expressly adopts nonretroactivity as
an alternative ground; p. 13 n.3 separately rejects extending the proposed
rule to FCA liability. codex-baseline identifies both, explains why changing
the broad collateral-consequence rule alone might not produce relief, and
does not confuse the proposed FCA extension with the date Padilla itself was
decided. It also distinguishes immigration-related and affirmative-misadvice
cases from the particular failure-to-warn claim, treats the petition's split
assertion as advocacy, and separates unresolved prejudice concerns from
holdings actually reached. Appendix A, p. 16 n.5 corroborates its statement
that the evidentiary-hearing issue was not reached.

The procedural account correctly treats the summer interval before the
scheduled conference as elapsed time, not relists, and distinguishes the
waiver from substantive opposition. These are sound record-based reasons
for a below-baseline probability. The remaining limitation is calibration:
the precise move to 1.5% has no measured conditional model, and the broader
split survey is not exhaustively verified. The candidate candidly says so.
The high score rewards supported analysis, not merely the correct denial;
the denial does not establish which obstacle motivated the Court.

## Leakage assessment

The log records forward mode and September 17 activity, before the October 5
resolution. It marks 31 of 35 calls captured (coverage about 0.886). Four web
rows are unobserved; despite the candidate's report of unusable results, I do
not treat those markers as proof of empty results. Their queries concern
Padilla, Chaidez, and old opinion URLs, not this petition's disposition.
The remaining visible activity concerns the staged petition and context,
historical statpack, general precedent verification, and output operations.
The related 2017 denial discussed in the rationale is expressly a different
petition. Neither log nor prose shows this event's denial being known or
presupposed. Retrieved outcome material is false, influence is
`not_applicable`, and leakage suspected is false.

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
