# Evaluation of claude-baseline

## Quantitative Summary

- **Stage:** Certiorari (`cert`), arrival moment (`evt-petition-arrival-disposition`).
- **Outcome:** Denied (`actual_disposition: "denied"`, `actual_granted: 0`) on November 9, 2026, after a single distribution (`distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`).
- **Prediction:** `predicted_disposition: "denied"`, `probability: 0.06` (`correct: 1`, `brier_score: 0.0036`).
- **Baseline:** Evaluated against the prediction-time statpack build (`ab6fb84c09a6`, digest `sha256:f8abdb31530370551ced5a16ef3db2ecf512b450e040799d9ec5d03b7b9f48c4`, carrying `sal-v3`, rather than the committed pack). The scored baseline and skill score are computed by the harness as the stamped segment base rate.

## Reasoning Quality (`reasoning_quality`: 0.88)

`claude-baseline` produced a well-reasoned, transparent analysis grounded in both the prediction-time statpack (`ab6fb84c09a6`, `sal-v3`) and the petition text:
1. **Base-rate decomposition:** `claude-baseline` accurately noted that under `sal-v3`, the `state` bracketed `reached` pool (`~36.6%`, `n=1425` across OT2017–OT2025) was nested with `high` and `federal` petitions, and carefully decomposed the terminal `state` figures (`17.5%` across the four floored Terms in `docs/salience.md`) to form an arrival class prior before applying case-specific discounts.
2. **Doctrinal and vehicle critique:** Having read the opening 300 lines of `petition.txt`, `claude-baseline` identified the lack of any federal or state high-court conflict (noting the petition's reliance on district-court decisions like *Bullock v. Carver* and *Sierra Melendez*), the doctrinal flaw of a territorial government claiming Fourteenth Amendment due-process and equal-protection rights for "the People of Guam," the in-house drafting by the Guam AG's office, and the fact-bound territorial statutory overlay. (Because it read only the first 300 lines of `petition.txt`, it did not reach the appended lower-court orders showing that the Guam Supreme Court dismissed only after the AG failed to appoint substitute counsel, which is why its probability of `0.06` remained slightly more generous than `codex-baseline`'s `0.025`.)
3. **Sub-claims:** Every secondary claim was explicitly reasoned and well calibrated, including `relist-increment: 0.97` (properly recognizing that from `distribution_count: 0`, any distribution to conference resolves the increment true).

## Predicted Reasoning (`predicted_reasoning_quality`: 0.92)

In `predicted_reasoning.md`, `claude-baseline` made specific, testable predictions that held up well against the realized docket:
- It predicted that the Court would deny certiorari in October or November 2026, and specifically anticipated that respondents might waive a response without the Court requesting one on its own. In fact, Respondent Chargualaf filed a waiver on August 26, 2026, the Court did not call for a response, and certiorari was denied on November 9, 2026.
- It predicted a single distribution with no relist, no CVSG, and no dissent from denial — all borne out (`distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`). A minor timing detail (expecting initial distribution for the late-September long conference or first October conference, whereas distribution occurred October 14 for the November 6 conference) did not affect the core trajectory or November denial window.

## Leakage Assessment

- **Mode:** `forward` (prediction timestamp `2026-08-16T11:48:19Z`; resolved `2026-11-09`).
- **Assessment:** `retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`. All tool calls were captured (`result_capture_coverage: 1.0`), ran nearly three months before the event resolved, and retrieved no documents dated after `2026-08-09`.
