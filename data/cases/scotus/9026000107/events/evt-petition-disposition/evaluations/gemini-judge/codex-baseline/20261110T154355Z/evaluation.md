# Evaluation of `codex-baseline`

## Overview and quantitative summary

- **Event:** `scotus/9026000107` / `evt-petition-disposition` (cert stage, distribution moment)
- **Outcome:** `denied` (`actual_granted = 0`), resolved on November 9, 2026 after 2 distributions (`distribution_count = 2`), no CVSG, and no noted dissent from denial.
- **Prediction:** `predicted_disposition = "denied"`, `probability = 0.22` (`correct = 1`, `brier_score = 0.0484`).
- **Base-rate calibration:** Graded against the statpack build in force at the candidate's run time (`1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, reconstructed via `fedcourts statpack-at`), which differs from the currently committed statpack (now under `sal-v8`). `codex-baseline` computed the exact risk-set (`reached`) base rate for `baseline` under `sal-v4` over OT2017–OT2025 from `statpack.json` (`638 / 12,720 = 0.050157`), matching the stamped segment base rate.

## Reasoning quality (`reasoning_quality = 0.93`)

`codex-baseline` produced an exceptionally rigorous and well-documented analysis in `reasoning.md`:

1. **Exact base-rate verification:** `codex-baseline` pooled the exact `prefix_est_grant_rate * prefix_weighted_resolved` counts across OT2017–OT2025 from the JSON artifact in force at prediction time and clearly explained why terminal relist and CVSG cuts represent terminal populations rather than forward transition probabilities.
2. **Primary-source verification of key precedent:** Rather than accepting the briefs' competing characterizations of *Pakdel v. City and County of San Francisco*, 594 U.S. 474 (2021), `codex-baseline` retrieved and read the opinion via CourtListener MCP, highlighting *Pakdel*'s distinction between administrative exhaustion and procedures that clarify whether an agency's initial position is truly conclusive.
3. **Careful record reading:** `codex-baseline` pinpointed the core vehicle vulnerability in the record—the factual dispute between the petition and the BIO over whether the County's letter was preliminary advice and whether an administrative waiver or category change was ever properly sought—alongside the unpublished status of the Fourth Circuit's decision and the overbreadth of Question 2's prudential-ripeness framing.

## Predicted reasoning (`predicted_reasoning_quality = 0.85`)

`codex-baseline`'s forecast document (`predicted_reasoning.md`) was specific, disciplined, and borne out on every realized dimension:

- **Disposition and procedural trajectory (borne out):** Correctly predicted denial (`P(grant) = 0.22`), accurately forecast **one further distribution** after the October 1 opposition was processed (`P = 0.94`, with a second additional distribution explicitly noted as less likely), and nailed the disposition window ("in late October or November 2026 following redistribution"—resolved November 9, 2026 after the October 21 redistribution).
- **CVSG and separate writings (borne out):** Correctly forecast no CVSG (`P = 0.04`) and an unexplained denial without a noted dissent or statement (`P(dissent | denial) = 0.20`).
- **Conditional grant framing (unresolved):** Provided a sound conditional analysis of how the Court would narrow review to Question 1 or consider summary vacatur under *Pakdel* if certiorari were granted. Because a cert denial resolves only disposition, distribution count, CVSG, timing, and separate writings—where `codex-baseline` was specific and right on every count—it earns **0.85**.

## Leakage assessment

- **Mode:** `forward` (prediction timestamp `2026-10-06T00:33:12Z`; event resolved `2026-11-09`).
- **Assessment:** `retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`. The retrieval log (`result_capture_coverage = 0.957`) shows two unobserved web searches for the 2021 *Pakdel* opinion and Supreme Court Rule 15, plus captured CourtListener MCP reads of *Pakdel* (`opinion_id = 4699044`). No current-case external queries were made and the case was unresolved at prediction time.
