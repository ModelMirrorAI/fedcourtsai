# Evaluation of `gemini-baseline` (`scotus/9026000204` — `evt-petition-arrival-disposition`)

## Quantitative Summary

- **Stage:** `cert` (arrival moment)
- **Predicted Disposition:** `granted` (P(grant) = 0.95)
- **Actual Disposition:** `granted` (`actual_granted` = 1, plenary review, resolved 2026-10-19 after 2 distributions)
- **`correct`:** 1
- **`brier_score`:** 0.0025
- **Baseline & Skill:** Because `gemini-baseline`'s scored prediction carries a frozen `context.band` (`federal` under `sal-v3`), `segment_base_rate`, `base_rate_basis`, and `brier_skill_score` are left null for the harness to stamp from the risk-set pool over the stamped segment base rate.

## Reasoning Quality (`0.78`)

`gemini-baseline` reached the right probability (0.95) and disposition (`granted`) on sound core fundamentals, but its `reasoning.md` is terse and omits important case-specific vehicle analysis:

1. **Core Signal Identification:** `gemini-baseline` properly anchored on the stamped segment base rate for the `federal` band and adjusted upward to 0.95 based on the three headline indicators: Solicitor General as petitioner, invalidation of a 160-year-old federal statute (26 U.S.C. § 5178(a)(1)(B)) under the enumerated powers / Necessary and Proper Clause, and a direct circuit split between the Fifth and Sixth Circuits.
2. **Shallow Record Engagement:** As reflected in both `retrieval_log.json` and `reasoning.md`, `gemini-baseline` read `questions-presented.txt` and `2026-08-19.json` but did not inspect `petition.txt`. Consequently, `reasoning.md` is a single brief paragraph that does not name the Sixth Circuit companion case (*Ream v. U.S. Department of the Treasury*, No. 26-93) or analyze the vehicle dynamics between the two pending petitions (such as *McNutt*'s undisputed standing and single Necessary and Proper question versus *Ream*'s standing dispute and Commerce Clause question). While `questions-presented.txt` sufficed to identify the overwhelming grant signals, deeper engagement with the provisioned petition would have strengthened the justification for the residual 5% risk and the relationship to the parallel petition.

## Leakage Assessment

- **Mode:** `forward` (prediction timestamp `2026-08-20T18:19:19Z` / log timestamps `2026-08-20T19:31Z–19:35Z`, nearly two months prior to the `2026-10-19` resolution).
- **Log Review:** All tool calls in `retrieval_log.json` are marked `unobserved` (0.0 capture coverage, standard for that engine's telemetry). Inspection of the queries shows reads of the arrival snapshot (`2026-08-19.json`), `questions-presented.txt`, `metrics/statpack.md`, a `fedcourts query` invocation with an invalid `--topic` flag, and a CourtListener search for `"Scott McNutt"`. Because the case was genuinely unresolved at docketing in August 2026, no outcome existed to leak.
- **Conclusion:** `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`.
