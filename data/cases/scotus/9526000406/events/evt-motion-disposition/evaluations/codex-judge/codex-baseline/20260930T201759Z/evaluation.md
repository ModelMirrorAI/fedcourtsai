# Evaluation: codex-baseline

## Outcome and numerical score

The interim outcome is `granted`, `actual_granted = 1`, resolved September 29, 2026. codex-baseline's `granted` prediction at 0.86 yields `correct = 1` and `(0.86 - 1)^2 = 0.0196`. The provisioned September 29 docket records both the stay and a certiorari grant; the latter does not turn this stay evaluation into cert or merits scoring.

## Reasoning quality: 0.90

The rationale carefully defines the substantive relief being forecast, separates it from an administrative pause, and explains why the earlier same-litigation interventions matter. It identifies the stay framework and connects the supplied application's legal theories and disruption allegations to it. Particularly strong is its treatment of evidence: the applicant's account is identified as advocacy, the absence of a respondent brief is not mistaken for a concession, and the lower-court reasoning is acknowledged to be known only through the government's description.

The analysis also gives substantive weight to the contrary case: a final judgment is not the earlier preliminary injunction, declaratory relief and vacatur raise a reserved question in the cited application, additional statutory grounds matter, and removal may produce irreversible harm. It explains the heterogeneous baseline and its coverage limitations without pretending that the probability adjustment is a fitted government-applicant effect.

The remaining limitation is the strength of the numerical conclusion relative to a one-sided document set. The rationale gives no empirical calibration for 0.86, and prior interim success does not by itself establish likely success on every changed ground. The realized grant rewards the probabilistic forecast but cannot retrospectively prove that degree of confidence or the predicted legal route. The disposing entry does not give a full explanation endorsing that route.

The grade applies only to `reasoning.md`. The separate forecast's timing, order form, and proposed grounds are contextual and unscored; the structured quantitative claims are reserved to the harness. No interim semantic grades or vote accuracy are written.

## Baseline

The interim baseline and Brier skill are for the harness to stamp, so neither appears in the JSON and `base_rate_basis` is null. In the supplied committed statpack, the strictly-prior pool for frozen application Term 2026 contains 296 resolved substantive applications in its nonzero 2024 and 2025 rows, above the 50-resolution floor. The interim section is present; no thin-pool or missing-section refusal is apparent. This evaluation did not refresh the corpus or establish remote freshness, and it has not observed the later stamp. The pool has uneven parse coverage, machine-matchable-resolution selection, and a broader population than the escalation-selected applications that receive forecasts.

## Leakage

The recorded mode is forward, and the September 27 log precedes the September 29 outcome. Of 38 calls, 36 carry captured results. The two unobserved web calls concern a historical general stay authority; the rationale's statement that they yielded nothing is not independently established by their missing results. Their queries nevertheless do not seek this application's outcome. The additional historical-authority lookup and provisioned-record reads provide no indicated target-outcome exposure. The prior 2025 stays are identified as different proceedings. A path-excluding file listing is not a read of the excluded labeling artifacts. The appropriate assessment is `not_applicable`, `retrieved_outcome_material = false`, and no leakage exclusion.
