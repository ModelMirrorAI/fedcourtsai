# Evaluation of codex-baseline

## Outcome and quantitative scores

This is a cert-stage cell. `outcome.json` records denial on October 5, 2026, and `actual_granted = 0`. codex-baseline's `denied` prediction is correct. P(any grant) = 0.12 yields **Brier = 0.0144**.

The prediction's frozen context is Term 2025, `elevated`, `sal-v4`, matching the committed statpack's salience-table heading. I pool the bracketed reached rates for every displayed Term strictly before 2025, rather than terminal rates or the evaluator's own context:

| Term | Reached rate | Weighted resolved n |
| --- | ---: | ---: |
| 2024 | 17.9% | 336 |
| 2023 | 17.5% | 354 |
| 2022 | 19.0% | 300 |
| 2021 | 20.5% | 342 |
| 2020 | 16.1% | 397 |
| 2019 | 13.8% | 334 |
| 2018 | 15.9% | 347 |
| 2017 | 17.5% | 400 |

The resulting **risk-set baseline is 484.386 / 2,810 = 0.17237935943060498**. The numerator is derived from rounded published rates, not an exact grant count. The caption renders ten of ten Terms, so there is no omitted rendered-window subset; Terms 2025 and 2026 do not enter the pool. Skill is `1 - 0.0144 / 0.17237935943060498^2 = 0.5153904514440745`. codex-baseline's reported exact-JSON anchor is approximately the same 17.2%; this evaluation follows the prompt's rendered Markdown surface. These are committed-pack calculations, not live corpus-state claims or evidence of cohort-wide calibration.

## Reasoning quality: 0.91

The rationale provides a strong, balanced explanation for moving below the appropriate risk-set anchor. It recognizes that the requested response and resulting redistribution are related signals, rather than independently proving sustained conference consideration. It analyzes each asserted conflict against the opposition and distinguishes a potentially broad legal issue from a case-specific disagreement over pleading and treatment.

Its treatment of vehicle problems is particularly careful: it labels the respondents' arguments as arguments, separates defendant-specific grounds, and does not promote undecided qualified-immunity or municipal-liability defenses into independent appellate holdings. The staged opposition expressly confirms that those issues were not reached. The discussion of the Taylor analogy also articulates procedural and constitutional differences, and acknowledges the unexamined photograph rather than resolving a disputed factual issue from advocacy alone.

The remaining limitation is quantitative: 12% is a reasoned adjustment, not an estimated conditional effect of the identified signals, and the record does not empirically establish its size. Some uncertainty necessarily remains because the lower-court reasoning is assessed largely through the parties' filings. These are modest limitations given the explicit qualification of the evidence. A correct denial does not establish that the Court adopted any of this analysis; the outcome gives no explanatory ground.

This grade concerns `reasoning.md` only. I do not reward the separate forecast's timing or score its proposed doctrinal path, and the quantitative claims are left to the harness.

## Leakage assessment

The log records forward mode and September 18 calls, before the October 5 denial. Result-capture coverage is 26/28, approximately 92.86%. Two web rows are **unobserved**, concerning a search for the 2020 Taylor opinion and its Supreme Court PDF. The candidate says those attempts supplied no usable evidence, but the harness does not independently establish empty or failed responses; I assess the rows from their historical-precedent targets, not that self-report. Captured lookup queries likewise identify Taylor rather than this petition's disposition.

The prose consistently treats Alexander as pending and identifies the old snapshot payload's limitations. There is no affirmative outcome-revealing material in the staged evidence. `retrieved_outcome_material = false`, influence is `not_applicable`, and leakage is not suspected. Collapsed `other` tool labels and identity redactions are not adverse evidence.

## Scope

Cert votes remain unscored, and this stage declares no semantic set. The optional stakes assessment is omitted because no independent score was fixed before seeing the candidate's score. Harness-owned provenance and claim-score fields are not written.
