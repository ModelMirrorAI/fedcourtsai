# Evaluation of `claude-baseline` (`scotus/9026000087` — `evt-petition-disposition`)

## Outcome and Quantitative Scoring

The Supreme Court denied certiorari on November 9, 2026 (`actual_disposition: "denied"`, `actual_granted: 0`), following the November 6, 2026 conference after a single distribution (`distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`).

- **Predicted disposition:** `denied` (`correct: 1`)
- **Predicted grant probability:** `0.004` (`brier_score: 0.000016`)
- **Base rate and skill:** Left for the harness (`stamp-cell`) to compute against the stamped segment base rate. Using `uv run fedcourts statpack-at`, `claude-baseline` ran against statpack build `0918fb18e74f` (`sha256:63295af7c6e50f69b51af1f372c8a86dd6e8a398f9e6bc408c56fd8af8ccaf4d`), whose `sal-v4` table matches the committed pack.

## Reasoning Quality (`0.90`)

`claude-baseline` delivered a sharp, well-calibrated, and methodologically sound analysis in `reasoning.md`:
1. **Proper base-rate anchoring:** `claude-baseline` properly identified the `sal-v4` `baseline` bracketed `reached` (risk-set) figures across strictly prior Terms (2017–2025) and pooled them (~640 grants over ~12,900 weighted petitions, ≈5%).
2. **Thorough synthesis of negative case markers:** It systematically explained why `P(grant)` belonged an order of magnitude below the class baseline (at 0.4%): the petitioner's pro se posture (`IsCounselofRecord: false`), the Fifth Circuit's unpublished per curiam summary-calendar affirmance with no poll on rehearing en banc, the underlying state-law hurricane insurance dispute (loss valuation and motel roof exclusion), the BIO's preservation objection that the three QPs were not raised below, the conflation of dismissal-sanction standards with Rule 37(c)(1) exclusion in the claimed circuit split, and the fact that the BIO was filed voluntarily without a call for response.
3. **Attention to docket details:** It also spotted the date discrepancy on the petition's docket entry (`Sep 06 2025` vs. `July 21, 2026` docketing date) and sensibly treated it as a docketing artifact rather than a jurisdictional bar.

## Predicted Reasoning (`0.85`)

`claude-baseline`'s `predicted_reasoning.md` was concrete, specific, and borne out across every testable dimension:
- Explicitly predicted that certiorari would be denied at the November 6, 2026 conference with no relist, going out on the conference's order list without drawing a second conference.
- Correctly predicted no CVSG and no dissent from denial.
- Provided a discriminating explanation of why QPs 2 and 3 were derivative or untenable compared to a narrowed QP 1 if the Court were to grant, and why no GVR or summary reversal was realistic in the absence of an intervening decision.

## Leakage Assessment

- **Mode:** `forward` (prediction placed October 12, 2026; event resolved November 9, 2026).
- **Assessment:** `retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`.
- **Notes:** All tool calls in `retrieval_log.json` were captured (`result_capture_coverage: 1.0`) and consisted solely of reading the provisioned files and the committed `metrics/statpack.md`.
