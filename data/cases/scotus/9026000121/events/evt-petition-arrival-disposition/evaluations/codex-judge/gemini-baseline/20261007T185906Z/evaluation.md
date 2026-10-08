# Evaluation: gemini-baseline

## Outcome and numerical score

This is a cert-stage arrival cell. The recorded disposition is `denied`, dated
October 5, 2026, and `actual_granted = 0`. gemini-baseline's prediction from run
`20260816T111104Z` also names `denied`, with P(grant) = 0.001. Consequently
`correct = 1` and `brier_score = (0.001 - 0)^2 = 0.000001`.

The denial record reports one distribution, no CVSG date, and no noted dissent
from denial, but no explanation of the Court's reasoning. A very small Brier
score here rewards the near-zero probability on this realized denial; it does
not demonstrate that such precision was justified ex ante or calibrated over
other cases.

## Reasoning quality: 0.64

The rationale correctly identifies the case's fact-bound, predominantly
state-law character, the absence of an identified split, and the resulting
case for a low grant probability. It names the prior-Term arrival risk-set
rate rather than presenting a terminal-band rate as an arrival baseline.
These are relevant and intelligible reasons for predicting denial.

The main limitation is the unsupported size and precision of the adjustment:
a roughly 5–7% anchor is reduced to 0.1% without a developed treatment of the
asserted federal due-process theory, the contested chronology underlying it,
the state appellate procedural posture, or a comparable-case basis for that
specific probability. Merely describing the questions as poorly drafted and
idiosyncratic does not supply that missing analysis. The provisioned petition
at printed pages 35–38 contains the intermediate court's evidentiary discussion
and the petitioner's competing employment-timing account; `reasoning.md` does
not engage that dispute or explain which uncertainties remain. This is a
sound directional account, but a relatively thin justification for an extreme
numerical forecast. The grade is not a penalty for brevity or for using fewer
tools; it reflects the missing reasoning needed to support the number.

The grade is restricted to the probability rationale in `reasoning.md`.
Structured claim probabilities and the separate `predicted_reasoning.md`
forecast are not scored or folded into this number. In particular, mechanical
handling of distribution/relist claims is left entirely to the harness.

## Baseline unavailable: salience-version mismatch

gemini-baseline freezes `context.band = baseline`, `salience_version = sal-v3`,
and Term 2026. The committed `metrics/statpack.md` table is headed `sal-v4`.
Its caption renders all 10 of 10 Terms; OT2017–OT2025 would be the strictly
prior-Term window, but a differently versioned band is not an eligible
baseline. The rate and skill fields are omitted and `base_rate_basis` is null.
Neither the approximate historical anchor in the rationale nor a terminal
fallback is substituted. The evaluator's terminal context is not used to
reassign the prediction's band. The mismatch is durably recorded in the
cell-level flag and is not counted against reasoning quality.

## Leakage and scoring boundaries

Both the prediction context and captured log designate forward mode. All 25
logged calls occurred on August 16, 2026, before the October 5 resolution.
Every result is marked `unobserved`, with capture coverage 0.0. This is a
telemetry limitation, not evidence of an empty or failed result and not itself
a defect. Assessment therefore rests on visible queries and the staged prose.
Queries target the provisioned snapshot directory, context, questions
presented, document manifest, instructions, schemas, and committed statpack;
no visible call searches externally for this case's result. The rationale and
forecast discuss the disposition as future, with no outcome-revealing fact.

On that evidence, the ordinary forward classification applies:
`retrieved_outcome_material = false`, `influenced_prediction = not_applicable`,
and `leakage_suspected = false`. This is not an assertion that uncaptured
snapshot contents were independently inspected or returned nothing; there is
simply no affirmative evidence overriding the genuinely-forward default.

Cert votes are unscored. No semantic set is declared, so no `semantic_grades`
block is written. Mechanical claim scores and provenance stamps are left to
the harness, and the forecast document is unscored.
