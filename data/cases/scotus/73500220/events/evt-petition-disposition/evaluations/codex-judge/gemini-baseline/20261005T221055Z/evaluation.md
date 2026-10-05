# Evaluation — gemini-baseline

Case: scotus/73500220; event: evt-petition-disposition; evaluation run:
20261005T221055Z. The blinded prediction is from run 20260917T181231Z.

## Outcome and quantitative assessment

The authoritative `outcome.json` records **denied**, `actual_granted: 0`,
resolved October 5, 2026. The provisioned October 5 snapshot also contains
that day's denial entry. The September 17 prediction called **denied** with
P(grant) = 0.001, so exact-label correctness is **1** and Brier is
(0.001 - 0)^2 = **1e-06**. Against the baseline below, Brier skill
is 1 - 1e-06 / (0.05120250431778929 - 0)^2 = **0.999618567588**.

## Reasoning quality: 0.40

The rationale identifies the response waiver and distinguishes a possible
call for response from an immediate grant. The supplied docket corroborates
the June 11 waiver. This is a relevant procedural reason for a low estimate,
and the predicted denial is correct. The rationale is concise and does not
pretend that it has an opposition brief.

However, the inference from that procedural fact to a 0.1% grant probability
is largely asserted. The document supplies neither a matching risk-set anchor
nor a measured waiver-conditioned rate, despite the frozen baseline context.
It does not explain why the probability should be so far below the roughly
5.12% strictly-prior risk-set rate. Calling the constitutional question
routine substitutes for engaging the petition's claimed doctrinal conflict,
its distinction between deportation and FCA liability, or the appended
opinion. In particular, it misses the explicit alternative nonretroactivity
holding in Appendix A, pp. 14–16, and the FCA-specific alternative ground in
p. 13 n.3. Those are record-specific reasons for doubting review, stronger
than an unexplained characterization of the subject as routine.

The excellent realized Brier score does not establish that such an extreme
probability was justified ex ante. The quality score reflects the limited
substantive analysis and unsupported numerical adjustment, not the length
of the document or the choice not to use external tools. No criticism of
its separate forecast document or ancillary claim probabilities enters this
score.

## Leakage assessment

The harness log records forward mode and 35 calls on September 17, all with
`result_capture: unobserved` (coverage 0.0). This is a visibility limitation,
not evidence that results were empty or a defect in the candidate. Visible
queries target local provisioning, context, schema/statpack inspection,
and artifact operations; no visible query seeks this petition's later
history or disposition. The rationale treats denial as prospective, rather
than reading the result from an already-decided case. No separate retrieval
note was staged; that absence is not proof of clean retrieval and is not
penalized. On the available evidence, retrieved outcome material is false,
influence is `not_applicable`, and leakage suspected is false. This is not
a certification of unobserved result contents.

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
