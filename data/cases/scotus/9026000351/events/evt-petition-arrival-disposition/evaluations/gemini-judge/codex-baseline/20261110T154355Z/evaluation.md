# Evaluation of `codex-baseline` (`scotus/9026000351`, `evt-petition-arrival-disposition`)

## Quantitative Summary

- **Stage:** `cert` (arrival moment)
- **Predicted disposition / probability:** `denied` (`probability = 0.008`, `granted = 0`)
- **Actual outcome:** `denied` (`actual_granted = 0`, resolved `2026-11-09` after 1 distribution, no CVSG, no noted dissent)
- **Correct:** `1`
- **Brier score:** `0.000064`
- **Baseline & skill:** `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left null for the harness to stamp from the committed statpack (`risk_set` basis under the prediction's frozen `sal-v4` `baseline` band). Because `codex-baseline` adjusted substantially downward from the stamped segment base rate toward 0 on a petition that was denied, its forecast achieves positive skill over the baseline.

## Reasoning Quality (`0.92`)

`codex-baseline` produced a rigorous, well-documented arrival analysis (`reasoning.md`):

1. **Base-rate anchoring:** Verified against the statpack build in force at prediction time (`2420d5dd72e1`, rebuilt via `uv run fedcourts statpack-at`), `codex-baseline` properly anchored on the private-petitioner `baseline` reached (risk-set) rate under `sal-v4` over prior Terms 2017–2025, explicitly distinguishing the arrival risk-set rate from the terminal baseline rate, the federal-petitioner column, and the terminal relist-zero cut.
2. **Case-specific vehicle analysis:** Reading `petition.txt` closely (at a vantage before `appendix.txt` was fetched on October 13, 2026), `codex-baseline` pinpointed the decisive obstacles to review:
   - Petition page 7, footnote 1 expressly conceded that neither court below addressed the constitutional challenge to 28 U.S.C. § 354(a)(2)(A)(i) and that it might not be reviewable at this stage.
   - The Court of Federal Claims dismissed for lack of a money-mandating claim under the Tucker Act, 28 U.S.C. § 1491(a)(1), and `codex-baseline` independently verified *United States v. Testan*, 424 U.S. 392, 398–402 (1976), via CourtListener to confirm that the petitioner's plain-text argument sought a sharp departure from settled jurisdictional doctrine.
   - The 28 U.S.C. § 455 recusal claim against the Federal Circuit panel did not cure the Court of Federal Claims' lack of subject-matter jurisdiction and presented no square circuit conflict.
   - The collateral third-party posture made this an unsuitable vehicle for addressing judicial-council disciplinary authority.
3. **Auxiliary claims and stakes:** `codex-baseline` reasoned clearly through the declared claims (`relist-increment` = 0.97 from a frozen count of zero because initial conference distribution counts as +1; `cvsg-increment` = 0.001 because the United States is respondent; `summary-disposition-route` = 0.25; `dissent-from-denial` = 0.015). Its `big_case_score` (`0.45`) somewhat overweights the abstract subject of judicial discipline relative to a hopeless pro se collateral Tucker Act vehicle, and `P(grant) = 0.008` is slightly conservative given the fatal jurisdictional and preservation bars, though well-calibrated in direction.

## Predicted reasoning (`0.85`)

`codex-baseline`'s forecast document (`predicted_reasoning.md`) was specific, disciplined, and borne out on every testable claim:

- **Disposition and ground (borne out):** Correctly predicted that the Court would deny certiorari and leave the Federal Circuit's disposition undisturbed without reaching the constitutionality of 28 U.S.C. § 354.
- **Procedural path and timing (borne out):** Correctly forecast that the petition would receive a single conference distribution after the October 16, 2026 response deadline and be denied in the November–December 2026 window without any further relist (`distribution_count: 1`, distributed October 21, 2026 for the November 6, 2026 Conference and denied November 9, 2026).
- **CVSG and separate writings (borne out):** Correctly forecast no CVSG (0.1%) because the United States is respondent, and an unexplained denial with no noted dissent or statement respecting denial (1.5%).
- **Conditional grant claims (unresolved):** Its conditional forecast that a grant would favor plenary consideration (75%) over summary disposition (25%) and focus on a narrowed recusal issue rather than § 354 was not tested because certiorari was denied.

The grade of `0.85` reflects that all four unconditional central claims were specific—including the post-October 16 single-distribution path and November–December 2026 denial window—and fully borne out, while recognizing that denial without CVSG or dissent after a single distribution is the standard trajectory for a pro se petition opposing the United States.

## Leakage Assessment

- **Mode:** `forward` (predicted `2026-09-27`, cutoff `2026-09-17`; resolved `2026-11-09`)
- **Retrieved outcome material:** `false`
- **Influenced prediction:** `not_applicable` (`leakage_suspected: false`)
- **Notes:** The prediction ran while the petition was newly docketed and unresolved. The harness-captured `retrieval_log.json` (`result_capture_coverage: 0.935`) confirms that `codex-baseline` read only the provisioned arrival record, schemas, and statpack, plus general legal lookups on *United States v. Testan* (CourtListener) and Supreme Court Rule 10.
