# Evaluation: codex-baseline

## Outcome and scoring scope

This is a cert-stage evaluation of the September 16, 2026 forward prediction. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`; the provisioned October 5 snapshot likewise records "Petition DENIED." A correct denial forecast does not establish why the Court denied review. No explanatory opinion or individual votes are supplied.

Only `reasoning.md` contributes to reasoning quality. The pointed-to `predicted_reasoning.md` was read for context, not scored. Quantitative claims are left to the harness; no claim scores, semantic grades, or cert-stage vote accuracy are written.

## Baseline and provenance

The prediction freezes `band = baseline`, `salience_version = sal-v4`, and Term 2025. The committed `metrics/statpack.md` heading matches sal-v4, so the basis is `risk_set`, using the bracketed baseline-band reached rates, not terminal rates or this evaluator's context. Every displayed strictly prior Term is included: 2017–2024. The table renders all 10 of its 10 Terms; 2025 and 2026 are excluded, so there is no rendered-window truncation to flag.

The displayed rate/weighted-denominator pairs are 4.7%/1643, 4.6%/1524, 4.6%/1399, 4.5%/1739, 5.6%/1500, 5.8%/1192, 5.9%/1312, and 5.7%/1271. Their resolved-weighted pool is 592.925 / 11580 = 0.05120250431778929. The numerator is derived from rounded displayed percentages, not an integer grant count. This is the committed live/historical-slice, denial-reweighted estimate, not a fresh corpus census. No corpus query was made, and corpus-wide refresh vintage was not established. Case-outcome provenance is the provisioned October 5 snapshot and outcome artifact.

Skill is `1 - Brier / baseline^2` because the observed binary is zero. These are descriptive scores for one resolved event, not evidence of calibration or population-level performance.

## Quantitative result

The candidate named `denied`, matching the outcome: **correct = 1**. Its grant probability was 0.006, giving **Brier = 0.000036** and **Brier skill = 0.9862684331659415**.

## Reasoning quality: 0.94

The analysis carefully separates the petitioners' allegations, the supplied docket's observations, and what cannot be verified without the appellate opinion. It identifies the petition's conceded failure to raise the constitutional issues as a vehicle risk without declaring an established jurisdictional bar. It differentiates the fact-bound requests from the broader statutory challenge, treats absent attention signals as limited observations rather than proof, and explains why constitutional stakes do not themselves overcome preservation and vehicle concerns.

It handles statistical conditioning particularly well: the frozen sal-v4 baseline uses strictly prior Terms, and the terminal relist/CVSG cuts are explicitly descriptive rather than direct prospective probabilities. Its stated unrounded JSON anchor, 593/11580, is slightly different from this evaluation's required rounded Markdown-table pool, 592.925/11580. This disclosed rounding difference is immaterial to the substantive adjustment and is not a salience-version or window mismatch.

The precedent discussion is bounded: it describes the protective-order analogy while distinguishing the federal prosecution and declining to treat that authority as dispositive of these state-law orders. The rationale also notes uncertain continuing effects of the two-year orders rather than asserting either mootness or extension. Those are useful limits on what the supplied record supports, not excuses to skip prediction.

The residual limitation is that 0.6% remains an explicitly judgmental adjustment from a broad historical band, not a validated conditional estimate. The one-sided petition and absent lower-court decision leave the key vehicle inference incompletely verified. The score rewards disciplined handling of those limits rather than the quantity of research or prose. The bare denial does not establish which rationale the Court accepted. No credit is drawn from the separately unscored forecast document or quantitative claims.

## Leakage

**Mode: forward; retrieved outcome material: false on the available evidence; influence: not_applicable; leakage suspected: false.** All logged calls occurred September 16, before the October 5 disposition. The queries concern provisioned materials, statistical context, general court rules, and the historical Rahimi precedent, not this petition's disposition or subsequent history. A file-discovery query explicitly excludes the prohibited labeling-artifact path; mentioning that exclusion is not reading the artifacts.

Capture coverage is **29/32 (90.625%)**. The three web rows are unobserved: although the candidate calls the attempts empty, the harness does not establish what they returned, so I assess their visible general-law targets rather than credit an asserted lack of results. Captured calls with neutral `other` labels remain interpretable through their queries; the label itself is not suspicious. No supplied metadata or prose shows the case was already decided at prediction time or that outcome material influenced it.
