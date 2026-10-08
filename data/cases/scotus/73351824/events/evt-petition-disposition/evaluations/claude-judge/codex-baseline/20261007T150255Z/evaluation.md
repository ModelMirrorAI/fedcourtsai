# Evaluation of codex-baseline — scotus/73351824, evt-petition-disposition

**Cell.** Cert stage (event `stage: cert`, moment `distribution`). Outcome: petition **denied** on 2026-10-05 at its first conference (one distribution, no relist, no CVSG, no noted dissent). `actual_granted` = 0.

**Prediction.** `denied`, P(grant) = 0.16, forward mode, frozen band `baseline` under `sal-v4`, Term 2025, distribution_count 1.

## Scores

- `correct` = 1 (predicted `denied`, actual `denied`).
- `brier_score` = (0.16 − 0)² = 0.0256.
- `segment_base_rate` = 0.0512, basis `risk_set`. Frozen `band: baseline` with `salience_version: sal-v4`, matching the statpack table heading, so the bracketed `reached` figures apply, pooled resolved-weighted over OT2017–OT2024 (the eight rendered Terms strictly before 2025; the table renders all 10 of the pack's Terms, so no window divergence): 593 / 11,580 = 0.05121. Baseline Brier 0.00262.
- `brier_skill_score` = 1 − 0.0256 / 0.00262 = **−8.76**. The highest probability in the cell, roughly three times the band rate, on a petition denied at first conference; the worst skill of the three.

## Reasoning quality: 0.70

Careful and well-sourced on the record, less convincing on the number.

Strengths:

- **Anchor computed exactly** from `statpack.json`: 593 / 11,580 = 5.12% over OT2017–OT2024 under `sal-v4`, with a correct explanation of why the terminal baseline rate would be the wrong population. The modern-cert whole-docket rate and the relist/CVSG cuts are quoted for orientation and explicitly not used mechanically.
- **It read the lower court's opinion** in Appendix A of the provisioned petition (pp. 1a–3a, 20a, 31a–36a) and used it as a check on the petition's advocacy: the Minnesota Supreme Court declined to reach equal protection because the applicants were not parties, vacated the intermediate court's constitutional discussion, affirmed a discretionary best-interests ruling, and found neither retaliatory animus nor decisive causation on the First Amendment theory, with other grounds for denying intervention. That is the decisive vehicle problem, correctly identified.
- **Honest limits.** It says it could not obtain the brief in opposition, that it did not read every appendix page, and that the 16% is "a judgmental calibration, not a fitted model."

Weaknesses:

- Having laid out the vehicle problem in detail, it still roughly tripled the band rate. The upward case is the Brackeen footnote, the response request, three amicus entries and the First Amendment theory. The candidate concedes the First Amendment claim's "factual premise is contested by the judgment itself" and that it found no square conflict, yet those concessions do not pull the number back toward the anchor. Given the outcome, the adjustment was poorly sized; given the reasoning's own content, it was also internally under-argued.
- Without the opposition brief it could not weigh the standing and redressability objections (enrollment, kinship placement) that the other side pressed, and it did not infer them from the record even though the appendix supplied the placement facts.
- A fair amount of the document is boilerplate on freshness, terminology and scope that carries no analytical weight. It also describes the event as a "legacy event" with no explicit stage or moment; the committed `event.yaml` carries `stage: cert` and `moment: distribution` today, though I cannot tell from the staged view what it carried at prediction time, so I do not penalize that.

The forecast document and claims block were read for context only and are not scored here.

## Leakage: forward, not applicable

Mode `forward`. The prediction was made on 2026-09-16, before the 2026-09-28 conference and the 2026-10-05 denial. `result_capture_coverage` is 0.9; the three unobserved rows are web searches and were graded on their queries: a Brackeen search, the Brackeen opinion PDF, and this docket's 2026-08-26 opposition PDF, which predates resolution and which the candidate reports returned no content. The CourtListener calls are a citation search for 599 U.S. 255 and four in-document searches of the 2023 Brackeen opinion. Everything else is the prompt, the provisioned record and the statpack. No call names this petition's disposition, no `retrieved_doc_date` is on or after 2026-10-05, and the prose explicitly discloses that no outcome or subsequent history was retrieved. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case: 0.50 (my own read)

The underlying ICWA equal-protection question is nationally significant, but this vehicle was a permissive-intervention denial affirmed on state-law grounds, and the Court denied it quietly at first conference with no separate writing. Disclosure: the candidates' `big_case_score` values were in the `prediction.json` files I read in a single pass before fixing this number, so the ordering the prompt asks for was not strictly kept; the read above is nonetheless mine and argued from the record and the outcome.

## Not written

No `vote_accuracy` (cert cell), no `semantic_grades` (no semantic set on a cert event), no `claim_scores`, `process_version`, or `base_rate_salience_version` (harness-stamped). `judgment_correct` is null (non-merits).
