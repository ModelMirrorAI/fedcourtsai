# Evaluation of `codex-baseline` (`scotus/9026000204` — `evt-petition-arrival-disposition`)

## Quantitative Summary

- **Stage:** `cert` (arrival moment)
- **Predicted Disposition:** `granted` (P(grant) = 0.95)
- **Actual Disposition:** `granted` (`actual_granted` = 1, plenary review, resolved 2026-10-19 after 2 distributions)
- **`correct`:** 1
- **`brier_score`:** 0.0025
- **Baseline & Skill:** Because `codex-baseline`'s scored prediction carries a frozen `context.band` (`federal` under `sal-v3`), `segment_base_rate`, `base_rate_basis`, and `brier_skill_score` are left null for the harness to stamp from the risk-set pool over the stamped segment base rate.

## Reasoning Quality (`0.96`)

`codex-baseline` delivered an exemplary arrival-stage analysis in `reasoning.md`:

1. **Proper Base-Rate Conditioning:** `codex-baseline` anchored appropriately on the stamped segment base rate for the `federal` band and explicitly avoided conditioning on the terminal zero-relist cut, recognizing that at the `arrival` moment (`distribution_count: 0`), future conference distributions are not yet observed.
2. **Doctrinal and Posture Analysis:** `codex-baseline` identified the three decisive factors elevating this petition well above the already-high federal petitioner baseline: (a) the Fifth Circuit's invalidation of a 160-year-old Act of Congress (26 U.S.C. § 5178(a)(1)(B)), (b) a square, acknowledged circuit split with the Sixth Circuit's decision eleven days later in *Ream v. U.S. Department of the Treasury*, 174 F.4th 480 (6th Cir. 2026), and (c) the Solicitor General petitioning on behalf of the United States.
3. **Vehicle Comparison:** Crucially, `codex-baseline` analyzed the specific vehicle advantages of *McNutt* relative to the pending companion petition in *Ream* (No. 26-93)—namely that standing was undisputed in *McNutt* (enhanced by associational standing), whereas *Ream* featured a standing dispute and an additional, unaddressed Commerce Clause question. That exact vehicle distinction became the centerpiece of the subsequent cert-stage briefing once the Brief in Opposition and Reply were filed, and the Court indeed granted *McNutt* after one relist (two distributions total).
4. **Calibrated Residual Uncertainty:** Retaining a 5% denial/dismissal tail for unseen BIO objections or companion-vehicle selection at the arrival moment was well-calibrated and thoroughly justified.

## Leakage Assessment

- **Mode:** `forward` (prediction timestamp `2026-08-20T19:09:45Z`, nearly two months prior to the `2026-10-19` resolution).
- **Log Review:** `retrieval_log.json` shows local reads of the provisioned arrival snapshot (`2026-08-19.json`), the petition text, and `metrics/statpack.md`, plus two CourtListener opinion searches constrained with `filed_before: "2026-08-20"` that surfaced only the April 2026 Fifth and Sixth Circuit opinions.
- **Conclusion:** `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`.
