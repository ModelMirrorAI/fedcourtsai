# Evaluation of codex-baseline — scotus/73452191, evt-petition-disposition

## Outcome and scores

Cert-stage cell, forward mode. The petition (No. 25-1356, Bernard v. Ignelzi) was distributed once, for the September 28, 2026 conference, and **denied on October 5, 2026** with no noted dissent. `actual_disposition` = `denied`, `actual_granted` = 0.

- `correct` = 1: the candidate predicted `denied`.
- `brier_score` = 0.015² = 0.000225.
- `segment_base_rate` = 0.0512 on the `risk_set` basis. The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack band table's heading, so the bracketed `reached` figure applies, pooled resolved-weighted over the rendered Terms strictly before Term 2025 (OT2017 through OT2024, eight rows, n = 11,580). The table renders all 10 Terms the pack holds, so the rendered window and the configured ten-Term lookback reach the same rows; no divergence to flag.
- `brier_skill_score` = 1 − 0.000225 / 0.0512² = 0.914.
- `vote_accuracy` omitted (cert cell). `judgment_correct` null. No `semantic_grades` block.

## Reasoning quality: 0.85

What is sound:

- Correct anchor, correctly derived: pools the sal-v4 baseline reached rates over OT2017–OT2024 to about 5.12% over n = 11,580, and says plainly that the figure is reconstructed from rounded percentages. It explicitly refuses the terminal-baseline rate and reads the relist and CVSG cuts as terminal descriptions rather than transition hazards, which is the right way to read them.
- Correct reading of the information boundary: one distribution, no relist, a waiver, no response request, no CVSG, and it uses the frozen band rather than reclassifying the caption because the respondent is a state judge.
- Identifies forfeiture as the dominant obstacle and explains why it matters at the cert stage: the Court would have to get past the preservation holding before reaching the immunity question, which makes this a poor vehicle regardless of the merits.
- Reads the claimed split critically. On the petition's own descriptions, Gibson and Rockett involve judges personally searching or jailing, King and Harper are factually distinct, and this judge is alleged to have directed deputies in connection with a pending matter. That is a careful and accurate deflation of the split.
- Retrieves Mireles v. Waco and uses it correctly: an order directing officers to bring someone before the court is a judicial act even if carried out unlawfully, and the Court there distinguished directing officers from personally performing their function. It caveats that the home-arrest setting could matter and labels the point as its own analogy.
- Disciplined about what is allegation versus finding, about what was and was not provisioned (no appendix, no lower-court opinions), and about the limits of its own retrieval.

Minor weaknesses:

- Underweights the structural point that the Court does not grant without a response: the waiver appears as "a docket showing waiver without further attention" rather than as the near-dispositive fact it is for a first-conference grant. The number landed in the right place anyway.
- The prose is long for the amount of movement it produces; the adjustment from 5.1% to 1.5% is called judgmental, which is honest, but the reader gets little sense of how the six factors are weighted against one another.

Net: a thorough, well-sourced rationale with the right dominant factor, the right anchor discipline, and honest epistemics.

## Leakage: not applicable

Forward cell; the prediction was created September 16, 2026, before the conference and the denial. The log (32 calls, capture coverage 0.9375) shows two web-search rows, both `unobserved` and graded on their queries: a Mireles citation search and a Fourth Circuit opinion URL, neither naming this petition. The CourtListener calls fetched Mireles v. Waco (1991) only. No call reached this case's docket or caption, no `retrieved_doc_date` falls on or after resolution, and no `data/qp-topics/` read appears. The reasoning discloses the attempts and states that no outcome was encountered; the forecast document predicts the denial timing as a forecast, not a retrieved date. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case: 0.15

Formed from the record: a doctrinally interesting but narrow judicial-immunity question, a single landlord-tenant contempt dispute, an unpublished forfeiture-based decision below, a waiver, and a first-conference denial with no writing. Legal-press interest at most. The staged prediction.json exposes each candidate's `big_case_score`, so the three scores were visible before this read was fixed; the read rests on the record, not on them.
