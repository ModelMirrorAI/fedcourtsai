# Evaluation: codex-baseline

## Outcome and arithmetic

The interim application was denied on October 1, 2026, with `actual_granted = 0`; the provisioned snapshot records denial by Justice Kagan. codex-baseline's `granted` label is incorrect, so correctness is **0**. Its probability of an unqualified grant was 0.58, yielding **(0.58 - 0)^2 = 0.3364** Brier loss. The bare denial does not disclose its doctrinal or equitable basis.

## Reasoning quality: 0.86

The rationale is careful and substantially grounded in the available record despite its wrong modal call. It separates applicant advocacy from established compliance, assesses institutional handover costs alongside ongoing injury to prisoners, and uses the district court's own contrary explanation rather than presenting one side's brief as fact. The application's Appendix 3–6 supports its account of monitors, intermediate measures, disputed compliance, and continuing constitutional injury. Appendix 1–2 supports its distinction between Judge Forrest's proposed administrative stay and substantive endorsement of the state's position, and its description of expedited appellate reconsideration.

It limits the independent weight placed on CASA, explains why an unconditioned application rate does not estimate this selected response-filed population, and candidly labels the large upward probability adjustment as judgmental. It also discloses the truncated application and missing opposition without pretending to know respondents' arguments. Those distinctions are material strengths, not rewards for document length.

The remaining weakness is calibration: the move to a grant lean is not supported by a measured reference class, and the emphasis on preserving state administration does not fully justify overcoming the concrete contrary findings and ongoing appellate process. Nonetheless, assigning substantial probability to denial while articulating those reasons is sound probabilistic analysis; the realized denial does not make the whole analysis unsound. The score concerns `reasoning.md` alone, excluding forecast-document accuracy, structured claims, and significance judgments.

## Baseline and scoring boundaries

This is interim, not cert or merits. Baseline and skill fields are omitted for the harness to stamp, and `base_rate_basis` is null. The committed interim section is present; its eligible prior-Term rows show 70 and 226 resolved substantive applications in 2024 and 2025 respectively, above the 50-resolution floor. Neither a missing section nor insufficient resolved sample is apparent. A final stamped value is not yet available. Interpretation remains limited by uneven parsing, selection for machine-matchable dispositions, ungranted withdrawals/dismissals, denial-first mixed orders, and the escalation-selected prediction population. The pack was not refreshed, and these statements do not represent current remote corpus counts.

Interim votes and the forecast document are unscored. There is no semantic set. Mechanical claim scores and provenance/context fields are left to the harness. No independent big-case assessment is supplied.

## Leakage

The log records forward mode and September 27 activity, before the October 1 resolution. Result capture covers 24 of 26 calls. The two unobserved calls sought a general stay-standard authority and the specific September 25 opposition linked in the snapshot. Their query subjects do not seek this application's outcome; their reported failures cannot independently be established from unobserved results. The reasoning acknowledges not reading the opposition and contains no disposition-dependent premise. There is no evidence of forward mis-provisioning or outcome influence: `not_applicable`, `leakage_suspected = false`. The September 26 baseline cutoff does not prohibit retrieval while a forward event remains unresolved.
