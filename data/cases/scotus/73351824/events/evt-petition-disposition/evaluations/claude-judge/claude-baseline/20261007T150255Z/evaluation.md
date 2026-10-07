# Evaluation of claude-baseline — scotus/73351824, evt-petition-disposition

**Cell.** Cert stage (event `stage: cert`, moment `distribution`). Outcome: petition **denied** on 2026-10-05 at its first conference (one distribution, no relist, no CVSG, no noted dissent). `actual_granted` = 0.

**Prediction.** `denied`, P(grant) = 0.08, forward mode, frozen band `baseline` under `sal-v4`, Term 2025, distribution_count 1.

## Scores

- `correct` = 1 (predicted `denied`, actual `denied`).
- `brier_score` = (0.08 − 0)² = 0.0064.
- `segment_base_rate` = 0.0512, basis `risk_set`. Frozen `band: baseline` with `salience_version: sal-v4`, matching the statpack table heading, so the bracketed `reached` figures apply, pooled resolved-weighted over OT2017–OT2024 (the eight rendered Terms strictly before 2025; the table renders all 10 of the pack's Terms, so no window divergence): 593 / 11,580 = 0.05121. Baseline Brier 0.00262.
- `brier_skill_score` = 1 − 0.0064 / 0.00262 = **−1.44**. Closest of the three candidates to the outcome and to the band rate, but still above the naive baseline on a petition that was denied, so negative skill.

## Reasoning quality: 0.82

The strongest analysis in the cell.

- **Anchor done correctly.** It names the version match, pools the bracketed `reached` figures over OT2017–OT2024 and arrives at ~5.1%, the same number the harness pools. The terminal relist-0 and no-CVSG cuts are used for shape only and labelled as such.
- **It read the adversarial briefing.** This is a forward cell, and the candidate fetched the brief in opposition (2026-08-26) and reply (2026-09-04) from the docket links in the provisioned snapshot. That let it identify what actually decided the petition: the question petitioners wanted decided was not decided below; the state high court affirmed a *permissive* intervention denial under a state rule, vacated the intermediate court's equal-protection discussion, and gave alternative grounds (the constitutional-challenge factor "was not the decisive factor"), so the adequate-and-independent-state-ground objection was strong; the reply conceded the most petitioners could win is a remand on intervention; standing and redressability were contestable (enrolled children, kinship placement, three years with the grandmother); no split. Each point is sourced to a filing.
- **Honest about the judgment calls.** The called-for-response multiplier is flagged as experience rather than a statpack figure, and the uncertainty section names what it could not see.

What holds it below 0.9:

- The response-request multiplier ("two to three") is asserted without support, and the "ordinarily 12–15%, halved by vehicle defects" arithmetic is a narrative fit rather than a derivation. The direction was right; the sizing is intuition.
- It says it could not see the Minnesota Supreme Court opinion because the appendix fell in the truncated part of `petition.txt`. Another candidate read Appendix A from the same provisioned file (pages 1a–36a), so the opinion was in the record and was missed. The analysis still reached the right holding through the briefs' quotations, but a direct read would have been the better evidence.

The forecast document and claims block were read for context only and are not scored here.

## Leakage: forward, not applicable

Mode `forward`. The prediction was made on 2026-09-16, before the 2026-09-28 conference and the 2026-10-05 denial. All 37 logged calls are captured. The two web fetches retrieved this docket's own brief in opposition and reply, filings that predate resolution and that the candidate disclosed in `reasoning.md` and `retrieval.md`; that is legitimate forward signal and a point for the cell's integrity, not leakage. Three CourtListener searches on ICWA returned no results, and two corpus citation lookups returned no rows. No `retrieved_doc_date` is on or after 2026-10-05, and the candidate states the case was pending for the 9/28 conference. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case: 0.50 (my own read)

The underlying ICWA equal-protection question is nationally significant, but this vehicle was a permissive-intervention denial affirmed on state-law grounds, and the Court denied it quietly at first conference with no separate writing. Disclosure: the candidates' `big_case_score` values were in the `prediction.json` files I read in a single pass before fixing this number, so the ordering the prompt asks for was not strictly kept; the read above is nonetheless mine and argued from the record and the outcome.

## Not written

No `vote_accuracy` (cert cell), no `semantic_grades` (no semantic set on a cert event), no `claim_scores`, `process_version`, or `base_rate_salience_version` (harness-stamped). `judgment_correct` is null (non-merits).
