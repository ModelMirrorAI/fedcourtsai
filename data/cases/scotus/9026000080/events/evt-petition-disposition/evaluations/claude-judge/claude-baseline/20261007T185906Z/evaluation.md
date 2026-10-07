# Evaluation: claude-baseline — Scroggins v. City of Shreveport, No. 26-80 (cert, petition disposition)

## Outcome and scores

The event is a **cert**-stage petition disposition. `outcome.json` records `denied` on 2026-10-05 (first order list of OT2026, after the September 28, 2026 long conference), `actual_granted` = 0, one distribution, no CVSG, no noted dissent from denial.

- `correct` = 1: `predicted_disposition` `denied` matches `actual_disposition` `denied` exactly.
- `brier_score` = (0.005 − 0)² = 0.000025.
- `segment_base_rate` = 0.0502, `base_rate_basis` = `risk_set`. The prediction's frozen context carries both `band: baseline` and `salience_version: sal-v4`, and the statpack's "Segment base rate by salience band (sal-v4)" heading matches that version. I pooled the bracketed `reached` figure resolved-weighted over every rendered Term strictly before the case's Term 2026 (OT2017–OT2025; the OT2026 row is empty): 638 grant-family outcomes over a weighted denominator of 12,720 = 0.05016, read from the per-Term `prefix_est_grant_rate` × `prefix_weighted_resolved` fields in `metrics/statpack.json`, which are the bracketed figures the table renders. The caption says "Most recent 10 of 10 Term(s)", so the rendered window is the pack's whole window and there is no lookback divergence to flag.
- `brier_skill_score` = 1 − 0.000025 / (0.0502 − 0)² = 0.990. The forecast was far sharper than the band baseline, and right.
- `vote_accuracy` omitted (cert stage; never scored). `judgment_correct` null. No `semantic_grades` (no semantic set on a cert event). `claim_scores` left to the harness.

## Reasoning quality: 0.90

This is the strongest analysis of the three. What drove the score:

- **Right anchor, correctly derived.** It pooled the sal-v4 baseline `reached` figure over OT2017–OT2025 and got ~5.0%, the same number I computed, and said explicitly that this is the yardstick the cell is scored against.
- **It went and read the decision under review.** Two CourtListener calls located and read the Fifth Circuit's published per curiam (filed 2025-10-17) and Judge Dennis's dissent. That surfaced the two facts that matter most for a cert forecast and that the petition itself conceals: the majority rested on **forfeiture** (an adequate independent ground the petition does not seriously engage), and the panel found that several authorities in the pro se appellate brief appeared to be fabricated. Both are serious vehicle defects, and the candidate reasoned correctly that they would deter even a Justice sympathetic to summary-judgment overreach.
- **Correct reading of the docket posture.** Respondent's waiver and the absence of a call for a response were weighed properly (the Court does not grant without first calling for a response, so a grant from this posture would have required a visible CFR entry). The inference that the long conference's grants are customarily released before the first October order list, so a 2026-10-04 snapshot showing nothing is mild further evidence of denial, is accurate and is drawn from the provisioned snapshot, not from retrieval.
- **The one upward factor was identified and sized sensibly.** It credited the panel dissent and the Tolan v. Cotton precedent for summary reversal of the Fifth Circuit on the summary-judgment standard, then distinguished Tolan on counsel, constitutional claim, and the absence of a forfeiture ground. That is the right structure: name the strongest case for the other side and explain why it does not carry.
- **Candid limits.** It flagged that it relied on the majority's characterisation rather than the briefs, noticed the odd March 23, 2026 filing-entry date against a June 2026 signature and July 17 docketing, and reasoned correctly that timeliness is unaffected either way.

What kept it below the top of the range: the pro se discount is asserted ("granted at a rate far below the band's") without a figure or source, and the 0.5% number is ultimately a judgment call stacked on several unquantified discounts. The direction and magnitude were well supported, but the chain from anchor to 0.005 is argued rather than measured. The rationale for the secondary numbers is coherent but is not scored here.

## Leakage: none; forward cell

`retrieval_log.json` records `mode: forward`, `result_capture_coverage` 1.0, 19 calls. The prediction was created 2026-10-04T20:33Z on the 2026-10-04 snapshot; the denial was entered 2026-10-05, so the outcome did not exist when the prediction was made. I checked for mis-provisioning: no call carries a `retrieved_doc_date` on or after 2026-10-05, the only dated retrieval is the Fifth Circuit opinion (2025-10-17, the decision under review), the corpus query was for 2020s granted priors generally, and nothing touched this case's Supreme Court docket, the order list, or `data/qp-topics/` (one shell call pipes `git status` output through a grep that names that path, which filters output lines and reads nothing under it). The candidate's `retrieval.md` matches the log. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My independent read is 0.03: one pro se plaintiff, one municipal fire department, fact-bound Title VII claims resolved below on forfeiture, no split, no amicus, denied without a noted dissent. The predictor's own stakes score was examined only after I formed mine.
