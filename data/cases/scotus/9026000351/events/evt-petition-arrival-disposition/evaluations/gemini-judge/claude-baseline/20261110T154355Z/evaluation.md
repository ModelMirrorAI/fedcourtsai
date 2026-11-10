# Evaluation of `claude-baseline` (`scotus/9026000351`, `evt-petition-arrival-disposition`)

## Quantitative Summary

- **Stage:** `cert` (arrival moment)
- **Predicted disposition / probability:** `denied` (`probability = 0.005`, `granted = 0`)
- **Actual outcome:** `denied` (`actual_granted = 0`, resolved `2026-11-09` after 1 distribution, no CVSG, no noted dissent)
- **Correct:** `1`
- **Brier score:** `0.000025`
- **Baseline & skill:** `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left null for the harness to stamp from the committed statpack (`risk_set` basis under the prediction's frozen `sal-v4` `baseline` band). Moving from the stamped segment base rate down to 0.5% on a denied petition yields positive skill over the baseline.

## Reasoning Quality (`0.94`)

`claude-baseline` delivered a sharp, thorough analysis of the arrival record (`reasoning.md`):

1. **Base-rate anchoring:** Verified against the statpack build in force at prediction time (`2420d5dd72e1`, rebuilt via `uv run fedcourts statpack-at`), `claude-baseline` properly anchored on the private-petitioner `baseline` reached (risk-set) rate under `sal-v4` across prior Terms 2017–2025 and checked the Federal Circuit originating-court cut before making its case-specific downward adjustment.
2. **Case-specific legal and vehicle analysis:** From the provisioned `petition.txt` and `questions-presented.txt`, supplemented by a CourtListener RECAP check confirming the petitioner's repeat pro se litigation in the Court of Federal Claims (`1:22-cv-00223`, `1:25-cv-00491`, `1:25-cv-02133`), `claude-baseline` identified every fatal vehicle defect:
   - The petitioner is a pro se paid litigant appealing a nonprecedential Federal Circuit summary affirmance of a Court of Federal Claims jurisdictional dismissal.
   - The petition's own footnote concedes that QP 1 (the constitutionality of 28 U.S.C. § 354(a)(2)(A)(i)) was not addressed by either court below and might not be reviewable.
   - QP 2 (recusal of the Federal Circuit under 28 U.S.C. § 455) had already been rejected by the Supreme Court when it denied the petitioner's mandamus petition in No. 25-1217 on June 22, 2026.
   - QP 3 asks the Court to overrule *United States v. Jones*, 131 U.S. 1 (1889), and more than a century of settled Tucker Act money-mandating doctrine without any circuit split.
3. **Calibration and transparency:** `claude-baseline` candidly noted that it read the first 30,000 characters of `petition.txt` and that its `fedcourts query` returned interim applications rather than cert petitions. Its auxiliary claim probabilities (`relist-increment` = 0.97, `cvsg-increment` = 0.01, `summary-disposition-route` = 0.35, `dissent-from-denial` = 0.02) were well-explained.

## Predicted reasoning (`0.90`)

`claude-baseline`'s forecast document (`predicted_reasoning.md`) anticipated the exact procedural path of the petition in impressive detail:

- **Waiver, conference timing, and disposition (borne out):** Specifically predicted that the Solicitor General would waive the right to respond, the Clerk would distribute the petition for an early-to-mid November 2026 conference, and the Court would deny certiorari on the order list immediately following that conference without calling for a response. Every step occurred as forecast: the United States waived on October 16, 2026, the petition was distributed on October 21, 2026 for the November 6, 2026 Conference, and certiorari was denied on November 9, 2026.
- **Single distribution / no relist (borne out):** Predicted that the petition would be distributed exactly once (`relist-increment` resolving yes from zero) with no relist (`distribution_count: 1`).
- **No CVSG and no dissent from denial (borne out):** Predicted no CVSG because the United States is respondent (`cvsg_date: null`) and no dissent or statement respecting denial (`noted_dissent_from_denial: false`).
- **Conditional grant analysis (unresolved):** Reasoned that if the Court took any question it would be QP 3 (the sole question actually decided below) rather than QP 1 or QP 2, with a cert-order route around one-third of the tiny grant probability; this remained untested upon denial.

The `0.90` score reflects how specifically `claude-baseline` called the entire post-arrival docket sequence (SG waiver, early-to-mid November conference distribution, no response call, single conference, immediate order-list denial without dissent) and correctly identified QP 3 as the only preserved issue below.

## Leakage Assessment

- **Mode:** `forward` (predicted `2026-09-27`, cutoff `2026-09-17`; resolved `2026-11-09`)
- **Retrieved outcome material:** `false`
- **Influenced prediction:** `not_applicable` (`leakage_suspected: false`)
- **Notes:** The prediction ran while the case was open and before any response, waiver, or distribution existed. The harness-captured `retrieval_log.json` (`result_capture_coverage: 1.0`) shows only local reads, one `fedcourts query` returning OT2025 interim applications, and CourtListener lookups returning pre-cutoff Court of Federal Claims RECAP dockets (`retrieved_doc_date: "2025-12-17"`).
