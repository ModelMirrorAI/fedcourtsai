# Evaluation of `codex-baseline`

## Overview and Quantitative Summary

- **Stage & Moment:** Cert stage (`cert`), arrival moment (`evt-petition-arrival-disposition`).
- **Outcome:** Petition `denied` on November 9, 2026 (`actual_granted = 0`, `distribution_count = 1`, `cvsg_date = null`, `noted_dissent_from_denial = false`).
- **Prediction:** `predicted_disposition = "denied"`, `probability = 0.03` (`correct = 1`, `brier_score = 0.0009`).
- **Baseline & Skill:** The harness stamps the segment base rate and Brier skill score from the committed statpack. `codex-baseline` appropriately conditioned on its frozen `baseline` arrival band (`sal-v4`, strictly prior Terms OT2017–OT2025) and adjusted downward below the stamped segment base rate to `0.03`.

## Reasoning Quality (`0.86`)

`codex-baseline` produced a careful, well-structured arrival analysis grounded in the full 40-page petition text and the `sal-v4` statpack in force at prediction time:

1. **Proper Arrival Conditioning:** `codex-baseline` accurately recognized that a private attorney challenging a circuit disciplinary order remains in the private (`baseline`) caption class despite naming the Ninth Circuit and Federal Respondents represented by the Solicitor General. It also properly distinguished the arrival `reached` rate from terminal band rates and from the terminal zero-relist bucket.
2. **Doctrinal and Vehicle Analysis:** `codex-baseline` checked *In re Ruffalo*, 390 U.S. 544, 550–552 (1968), via CourtListener and identified the key vehicle flaws apparent on the face of the petition: the petitioner admitted filing briefs with inaccurate authorities and defective verification, received an express show-cause order warning of suspension or disbarment, failed to request an evidentiary hearing on the original charges, and conceded (at pp. 25–26) that the cited proof-standard cases did not form an aligned constitutional split and were not even raised as a question presented. `codex-baseline` also astutely anticipated that the Ninth Circuit panel's reliance on the show-cause response could be viewed as aggravation or evidence of ongoing lack of candor on noticed charges rather than uncharged offenses, and that the AI-disclosure discussion could be read as an application of existing candor rules rather than a retroactive rulemaking under FRAP 47(b).
3. **Limitation:** `codex-baseline` candidly noted that the separate appendix had not yet been provisioned in `record/documents/` at the time of its run and appropriately discounted the petition's one-sided framing, though unlike `claude-baseline` it did not retrieve the published Ninth Circuit disciplinary order (*Lnu v. Blanche*, 177 F.4th 1014) via CourtListener to verify the panel's exact findings directly.

## Predicted Reasoning (`0.85`)

`codex-baseline`'s forecast document (`predicted_reasoning.md`) committed to three clear unconditional procedural calls and one properly hedged conditional branch:

- **Denial without separate writing (`borne-out`):** Correctly forecast that the Court would deny the petition without a noted dissent or statement respecting denial.
- **Single conference distribution and zero relists (`borne-out`):** Correctly forecast that the petition would be distributed once after the response stage and denied at that initial conference without a relist (and clearly explained why `relist-increment` at arrival measures at least one distribution from zero rather than a second conference).
- **No CVSG (`borne-out`):** Correctly explained that no CVSG would occur because the Solicitor General was already counsel of record for the federal respondents.
- **Conditional grant scope and route (`unresolved`):** Framed its discussion of Question 1 (*Ruffalo* notice) and plenary vs. summary review explicitly as conditional on a grant, which was never tested given the November 9, 2026 denial.

The forecast was specific, internally coherent, and borne out on every unconditional commitment, though slightly less specific on the response-waiver mechanism and conference timing than `claude-baseline`.

## Leakage Assessment

- **Mode:** `forward` (run on September 27, 2026, more than six weeks before the November 9, 2026 denial).
- **Findings:** Clean (`retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`). The harness log (`result_capture_coverage = 0.9375`) confirms that retrieval was limited to local provisioned inputs, two unobserved general web-search attempts for Court rules, and CourtListener lookups for *In re Ruffalo* (1968), with `data/qp-topics/` properly excluded via `-not -path`.
