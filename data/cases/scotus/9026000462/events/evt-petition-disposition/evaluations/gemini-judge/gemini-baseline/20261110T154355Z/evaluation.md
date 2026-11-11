# Evaluation of `gemini-baseline` (`scotus/9026000462`, `evt-petition-disposition`)

## Quantitative summary

- **Stage:** `cert` (discretionary petition for writ of certiorari, `moment: distribution`)
- **Predicted disposition / probability:** `denied`, `P(grant) = 0.005`
- **Actual outcome:** `denied` (`actual_granted = 0`) on `2026-11-09`
- **Correct:** `1`
- **Brier score:** `0.000025`
- **Segment base rate & skill score:** Left null for harness stamping against the stamped segment base rate.

## Analysis of `reasoning.md` (`reasoning_quality = 0.42`)

`gemini-baseline`'s `reasoning.md` is a single brief paragraph that reaches a sensible headline probability (`0.005`, `denied`) and identifies from a CourtListener search that the underlying dispute is a pro se individual's ADA claim from the Eighth Circuit with a response waiver, but makes two clear analytical errors:

1. **Misread base-rate anchor:** Grading `gemini-baseline`'s base-rate use against statpack build `1c4f550b7b75` (`sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, the `sal-v4` build in force at `20261008T143010Z`, rebuilt via `fedcourts statpack-at`, rather than the currently committed `sal-v8` statpack), `gemini-baseline` cited `~0.9%` as the prior-Term salience band rate for a paid `baseline` petition. In build `1c4f550b7b75`, `0.9%` is the single-Term (OT2025) *terminal* (unbracketed) rate for petitions ending in `baseline`, rather than the bracketed `reached` (risk-set) rate pooled across strictly prior Terms that a cell with a frozen band must anchor on and is scored against via the stamped segment base rate.
2. **Missed the `26M22` sealing-motion distribution sequence:** Unlike `claude-baseline` and `codex-baseline`, `gemini-baseline` did not notice from the docket entries that the September 9, 2026 distribution (for the September 28 conference) preceded the October 7 docketing of the cert petition and disposed of the linked sealing motion `26M22` on October 5. As a result, `gemini-baseline` treated the petition as having already undergone its conference distribution and set `relist-increment` to `0.02` (whereas `summary-disposition-route` was set to `0.05` in `prediction.json` despite `predicted_reasoning.md` stating that a grant "would likely be a summary disposition").

## Predicted reasoning (`predicted_reasoning_quality = 0.40`)

`gemini-baseline`'s `predicted_reasoning.md` is four sentences long and splits between a failed central procedural claim and generic, borne-out directional calls:

1. **No further distributions/relists before decision (`not-borne-out`):** `gemini-baseline` led with the claim that, having been distributed once so far, the petition would receive no further relists/distributions before a decision. Because the September 9 distribution was for sealing motion `26M22` and the cert petition was docketed on October 7, the petition was distributed a second time on October 14, 2026 for the November 6 conference (`signals.distribution_count: 2` in `outcome.json`).
2. **No call for a response and no CVSG (`borne-out`):** `gemini-baseline` forecast that the Court would not call for a response following respondent's waiver and would not issue a CVSG. Neither occurred.
3. **Denial without separate writing or dissent from denial (`borne-out`):** `gemini-baseline` forecast a denial without separate writing or dissent. The petition was denied on November 9, 2026 with `noted_dissent_from_denial: false`.
4. **Summary disposition conditional on a grant (`unresolved`):** `gemini-baseline` wrote in prose that if the Court granted review it would likely be a summary disposition (though recording `0.05` in `prediction.json`); because certiorari was denied, this conditional claim was not tested.

Under the rubric, because `gemini-baseline`'s lead procedural claim on further distributions failed and the remaining borne-out claims were brief and generic, `predicted_reasoning_quality` is `0.40`.

## Leakage assessment

- **Mode:** `forward` (predicted `2026-10-08T15:19:47Z`; resolved `2026-11-09`).
- **Assessment:** All 28 tool calls in `retrieval_log.json` have `result_capture: "unobserved"` (`result_capture_coverage: 0.0`), reflecting that engine's telemetry shape. Grading on the logged queries, the candidate read only the prompt, schemas, provisioned case files, and `metrics/statpack.md`, and queried CourtListener for `25-2561` and `Hauber` / `Honkamp`. The case was unresolved when the prediction ran and no outcome material existed. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`.
