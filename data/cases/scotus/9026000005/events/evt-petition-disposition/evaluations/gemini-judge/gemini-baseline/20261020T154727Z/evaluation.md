# Evaluation of `gemini-baseline` — `scotus/9026000005` (`evt-petition-disposition`)

## Outcome & Quantitative Summary

- **Stage:** `cert` (frozen `context.band`: `elevated`, `sal-v4`; segment base rate and Brier skill score are harness-stamped against the stamped segment base rate).
- **Predicted vs. Actual Disposition:** Predicted `denied` (`P(grant) = 0.02`) vs. actual `denied` (`actual_granted = 0`, resolved October 19, 2026, with no noted dissent from denial and `distribution_count = 2`).
- **Accuracy & Brier Score:** `correct = 1`, `brier_score = 0.0004`, the lowest Brier score among the three candidates and well ahead of the stamped segment base rate.

## Reasoning Quality (`0.68`)

`gemini-baseline` reached the best-calibrated headline probability (`0.02`), but its brief `reasoning.md` contained notable procedural and analytical gaps:

1. **Sound Core Legal Intuition:** `gemini-baseline` concisely identified that *Trump v. Slaughter* (2026) overruled *Humphrey's Executor*, that the D.C. Circuit had already ruled in the government's favor consistent with *Slaughter*, and that the Court had denied certiorari in the companion MSPB case (*Harris v. Bessent*) the day after *Slaughter*, leaving no circuit split or lower-court error to correct.
2. **Misreading of the Docket's Distribution History:** `gemini-baseline` treated the two distributions as a post-Long-Conference relist ("The petition is currently relisted (distributed twice). A relist at the Long Conference often indicates a Justice is writing a dissent from denial or a statement respecting denial"), overlooking that the August 5 distribution for the September 28 conference was interrupted on August 13 when the Court called for a response (filed September 14), making the September 30 entry the initial post-BIO distribution for the October 16 conference rather than a conference relist.
3. **Baseline & Scope Omissions:** In `reasoning.md`, `gemini-baseline` cited the terminal `relist-2` rate rather than anchoring on the reached `elevated` (`sal-v4`) band rate, did not address QP 2 (severance of agency functions vs. removal protections) or the SG's alternative request for summary affirmance, and omitted both `big_case_rationale` in `prediction.json` and any justification for its `big_case_score` in `reasoning.md`.

## Leakage Assessment

- **Mode:** `forward` (`2026-09-30`, before the October 16, 2026 conference and October 19, 2026 denial).
- **Findings:** `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. All logged tool calls carry `result_capture = unobserved` (`result_capture_coverage = 0.0`); inspecting the call queries confirms `gemini-baseline` read only the provisioned files (`event.yaml`, `record/context.json`, `questions-presented.txt`, `documents.json`, `petition.txt`, `brief-in-opposition.txt`), `metrics/statpack.md`, and schemas, with no external searches or prohibited path reads.
