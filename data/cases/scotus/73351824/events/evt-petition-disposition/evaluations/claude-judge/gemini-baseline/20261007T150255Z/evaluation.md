# Evaluation of gemini-baseline — scotus/73351824, evt-petition-disposition

**Cell.** Cert stage (event `stage: cert`, moment `distribution`). Outcome: petition **denied** on 2026-10-05 at its first conference (one distribution, no relist, no CVSG, no noted dissent). `actual_granted` = 0.

**Prediction.** `denied`, P(grant) = 0.12, forward mode, frozen band `baseline` under `sal-v4`, Term 2025, distribution_count 1.

## Scores

- `correct` = 1 (predicted `denied`, actual `denied`).
- `brier_score` = (0.12 − 0)² = 0.0144.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction's frozen context carries both `band: baseline` and `salience_version: sal-v4`, and the statpack's band table heading is `sal-v4`, so the bracketed `reached` figures apply. Pooled resolved-weighted over the rendered Terms strictly before 2025 (OT2017–OT2024, eight Terms; the table renders all 10 of the pack's Terms, so the rendered window is the whole pack and there is no window divergence to flag): 593 weighted grants over 11,580 weighted resolved = 0.05121. The baseline forecaster's Brier is 0.05121² = 0.00262.
- `brier_skill_score` = 1 − 0.0144 / 0.00262 = **−4.49**. The candidate more than doubled the band rate on a petition that was denied outright, so it scores well below the naive baseline.

## Reasoning quality: 0.45

What is sound: the band and its approximate pooled rate ("~4–6%") are identified; the upward factors cited (a requested response, three cert-stage amicus briefs, the Brackeen footnote inviting state-court challenges) are real docket facts; the downward factors (zero relists, a possibly messy procedural posture, the Court's possible preference for a vehicle where the state court reached the merits) are the right ones, and denial was the modal call.

What holds the grade down:

- The analysis is thin. It does not engage with the Minnesota Supreme Court's actual holding, which the provisioned `petition.txt` carried in Appendix A: permissive intervention denied under a state best-interests rule, affirmed for abuse of discretion, with the constitutional discussion vacated. The adequate-and-independent-state-ground problem and the alternative-holding structure, which were decisive, are not named.
- One framing is backwards: it calls the lower court's refusal to reach the constitutional challenge "a strong vehicle argument for the petitioners." It is the opposite, a vehicle defect, as the candidate half-acknowledges two sentences later. The tension is never resolved.
- The anchor is approximated rather than computed, and the move from ~5% to 12% rests on a list of signals with no attempt to size any of them.
- It describes Pacific Legal Foundation as counsel; the record shows PLF on an amicus brief ("Foster Parents, et al."), a smaller signal than counsel of record.

The forecast document and claims block were read for context only and are not scored here.

## Leakage: forward, not applicable

Mode `forward`. The prediction was made on 2026-09-16, before the 2026-09-28 conference and the 2026-10-05 denial. The log is 22 calls: prompt and AGENTS.md reads, the provisioned record and statpack, one `fedcourts query` for Brackeen context that the candidate reports failed, and output writes. No web or CourtListener calls. `result_capture_coverage` is 0.0 (the engine's standing shape), so every call was graded on its query; none targets this petition's disposition and no `retrieved_doc_date` falls on or after the resolution. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The staged set omits the candidate's `flags.json`, so this rests on the log and the prose.

## Big case: 0.50 (my own read)

The underlying ICWA equal-protection question is nationally significant, but this vehicle was a permissive-intervention denial affirmed on state-law grounds, and the Court denied it quietly at first conference with no separate writing. Disclosure: the candidates' `big_case_score` values were in the `prediction.json` files I read in a single pass before fixing this number, so the ordering the prompt asks for was not strictly kept; the read above is nonetheless mine and argued from the record and the outcome.

## Not written

No `vote_accuracy` (cert cell), no `semantic_grades` (no semantic set on a cert event), no `claim_scores`, `process_version`, or `base_rate_salience_version` (harness-stamped). `judgment_correct` is null (non-merits).
