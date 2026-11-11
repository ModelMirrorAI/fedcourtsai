# Evaluation of `codex-baseline` — `scotus/73548979` (`evt-petition-disposition`)

## Outcome and Quantitative Summary

On November 9, 2026, the Supreme Court denied the petition for a writ of certiorari in *Clemente Properties, Inc., et al. v. Pedro R. Pierluisi-Urrutia, et al.*, No. 25-1426 (`actual_disposition = "denied"`, `actual_granted = 0`, `noted_dissent_from_denial = false`, `signals.distribution_count = 3`, `signals.cvsg_date = null`).

- **`predicted_disposition`:** `"denied"` (`granted = 0`, `correct = 1`)
- **`probability`:** `0.32`
- **`brier_score`:** `(0.32 - 0)^2 = 0.1024`
- **Segment baseline and skill:** Stamped by the harness (`segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left null for `stamp-cell` to populate from the stamped segment base rate).

## Reasoning Quality (`reasoning_quality = 0.88`)

`codex-baseline`'s `reasoning.md` was exceptionally thorough and analytically precise (graded against the historical statpack build `886549a3ac32` in force at prediction time via `fedcourts statpack-at`):

- **Rigorous base-rate and docket hygiene:** `codex-baseline` verified from `metrics/statpack.json` the exact prior-Term (`2017–2024`) `sal-v4` `elevated` risk-set (`reached`) denominator and numerator, explicitly explained why the first relist should not be double-counted on top of the `elevated` band, and carefully verified that the "(Distributed)" notation on the September 21, 2026 supplemental brief entry was a filing annotation rather than a third conference distribution.
- **Comprehensive verification of authorities and filings:** `codex-baseline` downloaded and read the unprovisioned September 21, 2026 supplemental brief PDF from `supremecourt.gov` and used CourtListener (`opinion_id = 9393811`) to verify the majority framing and Justice Thomas's dissent in *Financial Oversight & Management Board for Puerto Rico v. Centro de Periodismo Investigativo, Inc.*, 598 U.S. 339 (2023). It also dissected the exact split authorities on Question 1 (*King v. United States*, *Jim Olive Photography*, and Judge Selya's concurrence in *Philip Morris v. Reilly*) and the BIO's preservation and *Penn Central* waiver objections on both questions.
- **Calibration assessment:** The only reason `reasoning_quality` sits slightly below `claude-baseline` (`0.88` vs. `0.92`) is that `codex-baseline` adjusted its top-line grant probability (`0.32`) and CVSG probability (`0.30`) upward rather aggressively from the stamped segment base rate. While `codex-baseline` articulated its decompose-and-sum reasoning transparently (roughly 12% direct grant after relist + 20% grant via a CVSG path or deeper relist cycle), attributing a 30% CVSG chance after a conference relist had already occurred gave too much weight to a party's 3-page Rule 15.8 supplemental brief quoting a USPTO Director's speech.

## Predicted Reasoning (`predicted_reasoning_quality = 0.90`)

`codex-baseline`'s `predicted_reasoning.md` was the most specific and accurate forecast document in the cohort:

1. **Exact procedural and timing call (`borne-out`):** `codex-baseline` led with a remarkably specific central claim: *"The central procedural path is one further relist, followed by denial without a separate writing, in late October or November 2026."* Every component of that sentence came true: the petition was relisted once more (distributed November 2 for the November 6 conference, taking `distribution_count` from 2 to 3) and was denied without a separate writing on November 9, 2026.
2. **Majority probability on `relist-increment` (`borne-out`):** `codex-baseline` was the only candidate to put >50% probability (`0.55`) on at least one further conference distribution beyond the two already recorded.
3. **Unadorned denial (`borne-out`):** `codex-baseline` explicitly forecast that a separate dissent or statement respecting denial was unlikely (`0.25`), reasoning that a relist triggered by the October 14 conference often ends in a quiet denial once chambers examine the preservation hurdles.

Because `codex-baseline` committed to a concrete, non-obvious multi-step procedural path (one further relist, followed by an unadorned denial in late October or November 2026) and every central claim held up, `predicted_reasoning_quality` earns `0.90`.

## Leakage Assessment

- **Mode:** `forward` (`run_id = 20261014T174020Z`, placed well before the `2026-11-09` resolution).
- **Findings:** `retrieval_log.json` (`result_capture_coverage = 0.949`) confirms that external calls were strictly limited to fetching the pre-cutoff September 21, 2026 supplemental brief PDF from `supremecourt.gov` and reading the 2023 *Financial Oversight* opinion (`598 U.S. 339`, `opinion_id = 9393811`) on CourtListener, all fully documented in `retrieval.md`. `retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`.
