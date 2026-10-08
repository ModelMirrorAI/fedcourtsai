# Evaluation: gemini-baseline

## Outcome and scoring scope

This is a cert-stage evaluation of the September 16, 2026 forward prediction. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`; the provisioned October 5 snapshot likewise records "Petition DENIED." A correct denial forecast does not establish why the Court denied review. No explanatory opinion or individual votes are supplied.

Only `reasoning.md` contributes to reasoning quality. The pointed-to `predicted_reasoning.md` was read for context, not scored. Quantitative claims are left to the harness; no claim scores, semantic grades, or cert-stage vote accuracy are written.

## Baseline and provenance

The prediction freezes `band = baseline`, `salience_version = sal-v4`, and Term 2025. The committed `metrics/statpack.md` heading matches sal-v4, so the basis is `risk_set`, using the bracketed baseline-band reached rates, not terminal rates or this evaluator's context. Every displayed strictly prior Term is included: 2017–2024. The table renders all 10 of its 10 Terms; 2025 and 2026 are excluded, so there is no rendered-window truncation to flag.

The displayed rate/weighted-denominator pairs are 4.7%/1643, 4.6%/1524, 4.6%/1399, 4.5%/1739, 5.6%/1500, 5.8%/1192, 5.9%/1312, and 5.7%/1271. Their resolved-weighted pool is 592.925 / 11580 = 0.05120250431778929. The numerator is derived from rounded displayed percentages, not an integer grant count. This is the committed live/historical-slice, denial-reweighted estimate, not a fresh corpus census. No corpus query was made, and corpus-wide refresh vintage was not established. Case-outcome provenance is the provisioned October 5 snapshot and outcome artifact.

Skill is `1 - Brier / baseline^2` because the observed binary is zero. These are descriptive scores for one resolved event, not evidence of calibration or population-level performance.

## Quantitative result

The candidate named `denied`, matching the outcome: **correct = 1**. Its grant probability was 0.001, giving **Brier = 0.000001** and **Brier skill = 0.9996185675879428**.

## Reasoning quality: 0.58

The short rationale correctly recognizes a private, fact-bound protective-order dispute, identifies the absence of a developed split in the supplied questions, and starts from roughly the appropriate 5.1% reached-band anchor. Its direction of adjustment is intelligible and its modal denial call is right.

The main defect is evidentiary: it affirmatively says the respondent waived a response. The supplied docket contains a response deadline and distribution, but no waiver entry, and no cited source supports a waiver. Other blinded candidates describe no recorded waiver. This is an unsupported assertion, not proof that a waiver never existed. Docket silence cannot bear the stronger factual claim the rationale makes.

The rationale also invokes a roughly 1.2% zero-relist rate without distinguishing the terminal-state cut from the live reached population or acknowledging the GVR component of the binary grant axis. It does not explain how those descriptive cuts yield the much more extreme 0.1% probability. Most importantly, it misses the petition's express account of nonpreservation of the constitutional claims, a more concrete vehicle concern than pro se status or domestic-relations subject matter alone. The captured query list includes the questions presented but no full-petition read; I do not treat unobserved results as proof of what was returned. The score reflects unsupported factual grounding and thin analytical development, not brevity, style, or the unscored forecast/claims.

## Leakage

**Mode: forward; retrieved outcome material: false on the available evidence; influence: not_applicable; leakage suspected: false.** All logged calls occurred September 16, before the recorded October 5 disposition. Queries show local input/statpack reads and output or validation operations, not an outcome search. The prose does not presuppose a decided result. Capture coverage is **0/25**: every call is marked unobserved. I cannot inspect those results and do not infer that they were empty. That telemetry limitation alone is neither leakage evidence nor a data defect. The unsupported waiver assertion affects reasoning quality, not leakage.
